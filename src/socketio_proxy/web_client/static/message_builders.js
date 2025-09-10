class MessageBuilder {
    constructor(event) {
        this.event = event;
        this.params = {};
    }

    getParamList() {
        return Object.keys(this.params);
    }

    build(jsonData) {
        return {
            event: this.event,
            data: jsonData
        };
    }
}

class AccountLoginBuilder extends MessageBuilder {
    constructor() {
        super('AccountLogin');
        this.params = {
            AccountName: '',
            Password: ''
        };
    }
}

class ChatRoomSearchBuilder extends MessageBuilder {
    constructor() {
        super('ChatRoomSearch');
        this.params = {
            Query: 'Catnest',
            Language: '',
            Space: '',
            Game: '',
            FullRooms: true,
            ShowLocked: true
        };
    }
}

class ChatRoomJoinBuilder extends MessageBuilder {
    constructor() {
        super('ChatRoomJoin');
        this.params = {
            Name: 'Catnest'
        };
    }
}

class ChatRoomLeaveBuilder extends MessageBuilder {
    constructor() {
        super('ChatRoomLeave');
        this.params = {};
    }
}

class ChatRoomChatBuilder extends MessageBuilder {
    constructor() {
        super('ChatRoomChat');
        this.params = {
            Content: '歪————————',
            Type: 'Chat'
        };
    }
}

export const messageBuilders = {
    'AccountLogin': new AccountLoginBuilder(),
    'ChatRoomSearch': new ChatRoomSearchBuilder(),
    'ChatRoomJoin': new ChatRoomJoinBuilder(),
    'ChatRoomLeave': new ChatRoomLeaveBuilder(),
    'ChatRoomChat': new ChatRoomChatBuilder()
};