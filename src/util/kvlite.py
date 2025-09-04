import asyncio
import aiosqlite
import msgpack
import time
import os
from typing import Optional, Any, List, Dict
from contextlib import asynccontextmanager

class KvLite:
    DEFAULT_NAMESPACE = "__default__"
    LOCK_POOL_SIZE = 32  # 定长锁池大小

    _SQL_SETUP = [
        "PRAGMA journal_mode = WAL;",
        "PRAGMA synchronous = NORMAL;",
        "PRAGMA cache_size = -4000;",  # 4MB cache
        """CREATE TABLE IF NOT EXISTS kv_store (
            group_name TEXT NOT NULL,
            key TEXT NOT NULL,
            value BLOB NOT NULL,
            expire_at REAL,
            PRIMARY KEY (group_name, key)
        )"""
    ]
    _SQL_INSERT = "INSERT OR REPLACE INTO kv_store (group_name, key, value, expire_at) VALUES (?, ?, ?, ?)"
    _SQL_SELECT_ONE = "SELECT value, expire_at FROM kv_store WHERE group_name = ? AND key = ?"
    _SQL_SELECT_MULTI_BASE = "SELECT key, value, expire_at FROM kv_store WHERE group_name = ? AND key IN "
    _SQL_DELETE_ONE = "DELETE FROM kv_store WHERE group_name = ? AND key = ?"
    _SQL_DELETE_MULTI_BASE = "DELETE FROM kv_store WHERE group_name = ? AND key IN "
    _SQL_LIST_GROUP = "SELECT key FROM kv_store WHERE group_name = ? AND (expire_at IS NULL OR expire_at > ?)"
    _SQL_CLEANUP = "DELETE FROM kv_store WHERE expire_at IS NOT NULL AND expire_at < ?"
    _SQL_SELECT_EXPIRATION = "SELECT expire_at FROM kv_store WHERE group_name = ? AND key = ?"
    _SQL_UPDATE_TTL = "UPDATE kv_store SET expire_at = ? WHERE group_name = ? AND key = ?"

    def __init__(self, db_path: str, pool_size: int = 16):
        self._db_path = db_path
        self._pool_size = pool_size
        self._pool: asyncio.Queue[aiosqlite.Connection] = asyncio.Queue()
        self._lock_pool = [asyncio.Lock() for _ in range(self.LOCK_POOL_SIZE)]
        self._cleanup_task: Optional[asyncio.Task] = None

    @classmethod
    async def create(cls, db_path: str, pool_size: int = 5, cleanup_interval: Optional[int] = 60):
        """
        工厂方法: 创建并初始化 KvLite 实例。
        """
        self = cls(db_path, pool_size)
        
        # 1. 初始化连接池
        for i in range(pool_size):
            try:
                # 只有第一个连接负责初始化建表
                is_setup_conn = (i == 0)
                conn = await aiosqlite.connect(db_path, timeout=10)
                if is_setup_conn:
                    await self._setup_database(conn)
                await self._pool.put(conn)
            except aiosqlite.Error as e:
                print(f"Error connecting to database: {e}")
                # 如果初始化失败，关闭已创建的连接
                await self.close()
                raise
        
        # 2. 启动定期清理任务
        if cleanup_interval and cleanup_interval > 0:
            self._cleanup_task = asyncio.create_task(self._periodic_cleanup(cleanup_interval))
            
        return self

    async def _setup_database(self, conn: aiosqlite.Connection):
        for statement in self._SQL_SETUP:
            await conn.execute(statement)
        await conn.commit()
    
    # 用上下文管理器来处理连接的获取和释放
    @asynccontextmanager
    async def _get_connection(self):
        """一个上下文管理器，用于安全地从连接池获取和归还连接。"""
        conn = await self._pool.get()
        try:
            yield conn
        finally:
            await self._pool.put(conn)

    async def _periodic_cleanup(self, interval: int):
        """
        定期清理过期的键值对。
        """
        while True:
            await asyncio.sleep(interval)
            try:
                async with self._get_connection() as conn:
                    await conn.execute(self._SQL_CLEANUP, (time.time(),))
                    await conn.commit()
            except Exception as e:
                print(f"Error during periodic cleanup: {e}")

    def _serialize(self, value: Any) -> bytes:
        return msgpack.packb(value, use_bin_type=True)

    def _deserialize(self, value_blob: bytes) -> Any:
        return msgpack.unpackb(value_blob, raw=False)

    def _get_namespace(self, group: Optional[str]) -> str:
        return group if group is not None else self.DEFAULT_NAMESPACE

    async def _get_lock_for_namespace(self, namespace: str) -> asyncio.Lock:
        """
        根据 namespace 的哈希值确定锁的下标，避免全局锁。
        """
        namespace_hash = hash(namespace)
        lock_index = namespace_hash % self.LOCK_POOL_SIZE
        return self._lock_pool[lock_index]

    async def incr(self, key: str, group: Optional[str] = None, amount: int = 1) -> int:
        """
        原子性地增加一个键的值。如果键不存在，则从 0 开始。
        此操作会保留键原有的过期时间。
        """
        namespace = self._get_namespace(group)
        namespace_lock = await self._get_lock_for_namespace(namespace)
        async with namespace_lock:
            async with self._get_connection() as conn:
                async with conn.execute(self._SQL_SELECT_ONE, (namespace, key)) as cursor:
                    row = await cursor.fetchone()
                
                current_num = 0
                original_expire_at = None
                if row:
                    value_blob, expire_at = row
                    if not expire_at or time.time() < expire_at:
                        original_expire_at = expire_at
                        try:
                            val = self._deserialize(value_blob)
                            if not isinstance(val, int):
                                raise TypeError(f"Value for key '{key}' in group '{namespace}' is not an integer")
                            current_num = val
                        except (msgpack.exceptions.UnpackException, TypeError):
                            raise TypeError(f"Value for key '{key}' in group '{namespace}' is not an integer")
        
                new_num = current_num + amount
                await conn.execute(self._SQL_INSERT, (namespace, key, self._serialize(new_num), original_expire_at))
                await conn.commit()
                return new_num

    async def decr(self, key: str, group: Optional[str] = None, amount: int = 1) -> int:
        """原子性地减少一个键的值。是 incr(..., amount=-amount) 的语法糖。"""
        return await self.incr(key, group, -amount)

    async def setnx(self, key: str, value: Any, group: Optional[str] = None, ttl: Optional[int] = None) -> bool:
        """
        Set If Not Exists. 如果键不存在，则设置它并返回 True。如果键已存在，则什么都不做并返回 False。
        """
        namespace = self._get_namespace(group)
        namespace_lock = await self._get_lock_for_namespace(namespace)
        async with namespace_lock:
            async with self._get_connection() as conn:
                async with conn.execute(self._SQL_SELECT_EXPIRATION, (namespace, key)) as cursor:
                    row = await cursor.fetchone()
                
                key_exists = False
                if row:
                    expire_at, = row
                    if not expire_at or time.time() < expire_at:
                        key_exists = True
                
                if key_exists:
                    return False
                
                expire_at = (time.time() + ttl) if ttl and ttl > 0 else None
                await conn.execute(self._SQL_INSERT, (namespace, key, self._serialize(value), expire_at))
                await conn.commit()
                return True

    async def ttl(self, key: str, group: Optional[str] = None) -> int:
        """
        获取键的剩余生存时间（秒）。
        返回: -1 (无过期), -2 (不存在或已过期), >=0 (剩余秒数)。
        """
        namespace = self._get_namespace(group)
        async with self._get_connection() as conn:
            async with conn.execute(self._SQL_SELECT_EXPIRATION, (namespace, key)) as cursor:
                row = await cursor.fetchone()

        if not row:
            return -2
        
        expire_at, = row
        if expire_at is None:
            return -1
        
        remaining = expire_at - time.time()
        return int(remaining) if remaining > 0 else -2

    async def touch(self, key: str, group: Optional[str] = None, ttl: int = 60) -> bool:
        """
        更新一个键的过期时间而不改变其值。
        返回 True 如果键存在并被更新，否则返回 False。
        """
        namespace = self._get_namespace(group)
        namespace_lock = await self._get_lock_for_namespace(namespace)
        new_expire_at = time.time() + ttl
        async with namespace_lock:
            async with self._get_connection() as conn:
                cursor = await conn.execute(self._SQL_UPDATE_TTL, (new_expire_at, namespace, key))
                await conn.commit()
                return cursor.rowcount > 0

    async def getset(self, key: str, value: Any, group: Optional[str] = None, ttl: Optional[int] = None) -> Optional[Any]:
        """
        原子性地设置一个键的新值，并返回它的旧值。如果键不存在，返回 None。
        """
        namespace = self._get_namespace(group)
        namespace_lock = await self._get_lock_for_namespace(namespace)
        async with namespace_lock:
            async with self._get_connection() as conn:
                async with conn.execute(self._SQL_SELECT_ONE, (namespace, key)) as cursor:
                    row = await cursor.fetchone()
                
                old_value = None
                if row:
                    value_blob, expire_at = row
                    if not expire_at or time.time() < expire_at:
                        old_value = self._deserialize(value_blob)
                
                expire_at = (time.time() + ttl) if ttl and ttl > 0 else None
                await conn.execute(self._SQL_INSERT, (namespace, key, self._serialize(value), expire_at))
                await conn.commit()
                return old_value

    async def _delete_keys(self, conn: aiosqlite.Connection, namespace: str, keys: List[str]) -> int:
        """在当前事务中删除一个或多个键，返回删除的行数。"""
        if not keys:
            return 0
        if len(keys) == 1:
            sql = self._SQL_DELETE_ONE
            params = [namespace, keys[0]]
        else:
            placeholders = ', '.join('?' for _ in keys)
            sql = self._SQL_DELETE_MULTI_BASE + f"({placeholders})"
            params = [namespace] + keys
        
        cursor = await conn.execute(sql, params)
        return cursor.rowcount

    async def set(self, key: str, value: Any, group: Optional[str] = None, ttl: Optional[int] = None):
        namespace = self._get_namespace(group)
        namespace_lock = await self._get_lock_for_namespace(namespace)
        expire_at = (time.time() + ttl) if ttl and ttl > 0 else None
        serialized_value = self._serialize(value)

        async with namespace_lock:
            async with self._get_connection() as conn:
                await conn.execute(self._SQL_INSERT, (namespace, key, serialized_value, expire_at))
                await conn.commit()

    async def get(self, key: str, group: Optional[str] = None) -> Optional[Any]:
        namespace = self._get_namespace(group)
        async with self._get_connection() as conn:
            async with conn.execute(self._SQL_SELECT_ONE, (namespace, key)) as cursor:
                row = await cursor.fetchone()

            if not row:
                return None
            
            value_blob, expire_at = row
            if expire_at and time.time() > expire_at:
                await self._delete_keys(conn, namespace, [key]) # 传入 conn
                await conn.commit()
                return None
            
            return self._deserialize(value_blob)

    async def hset(self, key: str, field: str, value: Any, group: Optional[str] = None) -> int:
        """
        为一个哈希(key)中的字段(field)赋值。
        返回: 1 如果字段是新创建的，0 如果字段是被覆盖的。
        """
        namespace = self._get_namespace(group)
        namespace_lock = await self._get_lock_for_namespace(namespace)
        async with namespace_lock:
            async with self._get_connection() as conn:
                async with conn.execute(self._SQL_SELECT_ONE, (namespace, key)) as cursor:
                    row = await cursor.fetchone()

                the_hash = {}
                original_expire_at = None
                
                if row:
                    value_blob, expire_at = row
                    original_expire_at = expire_at
                    if not expire_at or time.time() < expire_at:
                        val = self._deserialize(value_blob)
                        if not isinstance(val, dict):
                            raise TypeError(f"Value for key '{key}' in group '{namespace}' is not a hash/dictionary.")
                        the_hash = val

                is_new_field = field not in the_hash
                the_hash[field] = value
                
                await conn.execute(self._SQL_INSERT, (namespace, key, self._serialize(the_hash), original_expire_at))
                await conn.commit()
                
                return 1 if is_new_field else 0

    async def hget(self, key: str, field: str, group: Optional[str] = None) -> Optional[Any]:
        """
        获取哈希(key)中指定字段(field)的值。
        """
        namespace = self._get_namespace(group)
        async with self._get_connection() as conn:
            async with conn.execute(self._SQL_SELECT_ONE, (namespace, key)) as cursor:
                row = await cursor.fetchone()

            if not row:
                return None
            
            value_blob, expire_at = row
            if expire_at and time.time() > expire_at:
                return None
            
            val = self._deserialize(value_blob)
            if not isinstance(val, dict):
                raise TypeError(f"Value for key '{key}' in group '{namespace}' is not a hash/dictionary.")
            
            return val.get(field)

    async def hgetall(self, key: str, group: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        获取哈希(key)中所有的字段和值。
        """
        namespace = self._get_namespace(group)
        async with self._get_connection() as conn:
            async with conn.execute(self._SQL_SELECT_ONE, (namespace, key)) as cursor:
                row = await cursor.fetchone()

            if not row:
                return None
            
            value_blob, expire_at = row
            if expire_at and time.time() > expire_at:
                await self._delete_keys(conn, namespace, [key])
                await conn.commit()
                return None
            
            val = self._deserialize(value_blob)
            if not isinstance(val, dict):
                raise TypeError(f"Value for key '{key}' in group '{namespace}' is not a hash/dictionary.")
            
            return val

    async def stats(self) -> Dict[str, Any]:
        """
        返回关于键值存储的统计信息。
        """
        async with self._get_connection() as conn:
            async with conn.execute("SELECT COUNT(*) FROM kv_store") as cursor:
                total_keys = (await cursor.fetchone())[0]

            keys_per_group = {}
            q_groups = "SELECT group_name, COUNT(*) FROM kv_store GROUP BY group_name"
            async with conn.execute(q_groups) as cursor:
                async for group_name, count in cursor:
                    keys_per_group[group_name] = count
            
            try:
                disk_usage_bytes = os.path.getsize(self._db_path)
            except (OSError, TypeError):
                disk_usage_bytes = -1

            return {
                "total_keys": total_keys,
                "keys_per_group": keys_per_group,
                "disk_usage_bytes": disk_usage_bytes
            }

    async def mset(self, items: Dict[str, Any], group: Optional[str] = None, ttl: Optional[int] = None):
        if not items:
            return

        namespace = self._get_namespace(group)
        namespace_lock = await self._get_lock_for_namespace(namespace)
        expire_at = (time.time() + ttl) if ttl and ttl > 0 else None

        data_to_insert = [
            (namespace, key, self._serialize(value), expire_at)
            for key, value in items.items()
        ]

        async with namespace_lock:
            async with self._get_connection() as conn:
                await conn.executemany(self._SQL_INSERT, data_to_insert)
                await conn.commit()

    async def mget(self, keys: List[str], group: Optional[str] = None) -> Dict[str, Any]:
        if not keys:
            return {}

        namespace = self._get_namespace(group)
        placeholders = ', '.join('?' for _ in keys)
        sql = self._SQL_SELECT_MULTI_BASE + f"({placeholders})"
        
        results = {}
        keys_to_delete = []

        async with self._get_connection() as conn:
            async with conn.execute(sql, [namespace] + keys) as cursor:
                async for row in cursor:
                    key, value_blob, expire_at = row
                    if expire_at and time.time() > expire_at:
                        keys_to_delete.append(key)
                    else:
                        results[key] = self._deserialize(value_blob)

            if keys_to_delete:
                await self._delete_keys(conn, namespace, keys_to_delete)
                await conn.commit()
            
        return results

    async def delete(self, key: str, group: Optional[str] = None) -> bool:
        namespace = self._get_namespace(group)
        namespace_lock = await self._get_lock_for_namespace(namespace)
        async with namespace_lock:
            async with self._get_connection() as conn:
                deleted_count = await self._delete_keys(conn, namespace, [key])
                await conn.commit()
                return deleted_count > 0

    async def list_group(self, group: Optional[str] = None) -> List[str]:
        namespace = self._get_namespace(group)
        async with self._get_connection() as conn:
            async with conn.execute(self._SQL_LIST_GROUP, (namespace, time.time())) as cursor:
                rows = await cursor.fetchall()
                return [row[0] for row in rows]

    async def close(self):
        """
        关闭连接池和清理任务。
        """
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            
        while not self._pool.empty():
            conn = await self._pool.get()
            await conn.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()