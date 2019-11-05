
let APP = {
    /**
     * WebSocket for this app.
     */
    ws: null,

    /**
     * Widgets can use wsopen.done callback to ensure
     * the WebSocket is open.
     */
    wsopen: $.Deferred(),

    connect: function(url="ws://localhost:8881/websocket") {
        this.ws = new WebSocket(url);

        // Runs when the WebSocket connects. Resolved the wsopen
        // promise/deferred.
        this.ws.onopen = function() {
            console.log("[APP] Websocket connection ready.");
            this.wsopen.resolve();
        }.bind(this);

        // Set WebSocket handler.
        this.ws.onmessage = this.onWsMessage.bind(this);
    },

    /**
     * Handler for WebSocket messages. These are routed to the
     * widget indicated by the messgae's id.
     * @param {Event} event
     */
    onWsMessage(event) {
        let message = JSON.parse(event.data);

        console.log("[APP] Message received: ", message);

        $('#' + message.id).trigger('message', message);
    },

    send: function(message) {
        this.ws.send(JSON.stringify(message));
    }
};

/**
 * For use with Widget2 widgets.
 */
let APP2 = {
    /**
     * WebSocket for this app.
     */
    ws: null,

    /**
     * Widgets can use wsopen.done callback to ensure
     * the WebSocket is open.
     */
    wsopen: $.Deferred(),

    connect: function(url="ws://localhost:8881/websocket") {
        this.ws = new WebSocket(url);

        // Runs when the WebSocket connects. Resolved the wsopen
        // promise/deferred.
        this.ws.onopen = function() {
            console.log("[APP] Websocket connection ready.");
            this.topwidget = new Widget2("topwidget", {}, this);
            this.topwidget.setElement($('body'));

            this.wsopen.resolve();
        }.bind(this);

        // Set WebSocket handler.
        this.ws.onmessage = this.onWsMessage.bind(this);
    },

    /**
     * Handler for WebSocket messages. These are routed to the
     * widget indicated by the messgae's id.
     * @param {Event} event
     */
    onWsMessage(event) {
        let message = JSON.parse(event.data);

        console.log("[APP] Message received: ", message);

        this.topwidget.local_deliver(message);

        // if (message.id === 'topwidget') {
        //     this.topwidget.onMessage(event, message);
        // }
    },

    send: function(message) {
        this.ws.send(JSON.stringify(message));
    },

    deliver: function(message) {
        this.send(message);
    },

    outbox: []

};

// class APP2 extends Widget2 {
//
//     constructor(url="ws://localhost:8881/websocket") {
//
//         super('topwidget', {});
//         this.wsopen = $.Deferred();
//
//         this.connect(url);
//     }
//
//     connect(url="ws://localhost:8881/websocket") {
//         this.ws = new WebSocket(url);
//
//         // Runs when the WebSocket connects. Resolved the wsopen
//         // promise/deferred.
//         this.ws.onopen = function() {
//             console.log("[APP] Websocket connection ready.");
//             this.wsopen.resolve();
//         }.bind(this);
//
//         // Set WebSocket handler.
//         this.ws.onmessage = this.onWsMessage.bind(this);
//     }
//
//     /**
//      * Handler for WebSocket messages. These are routed to the
//      * widget indicated by the messgae's id.
//      * @param {Event} event
//      */
//     onWsMessage(event) {
//         let message = JSON.parse(event.data);
//
//         console.log("[APP] Message received: ", message);
//
//         $('#' + message.id).trigger('message', message);
//     }
//
//     send(message) {
//         this.ws.send(JSON.stringify(message));
//     }
//
// };


class Widget {

    /**
     *
     * @param {string} id
     * @param {jQuery.Deferred} wspromise - Promise to wait on before starting
     *  communication with the server.
     */
    constructor(id, wspromise=null) {
        this.id = id;
        this.node = $("#" + this.id);

        if (wspromise === null) {
            this.onCommReady();
        }
        else {
            wspromise.done(this.onCommReady.bind(this));
        }

        this.node.on("message", this.onMessage.bind(this));

        this.msgHandlers = {
            children: [this.onChildren.bind(this)],
            append: [this.onAppendChild.bind(this)],
            remove: [this.onRemoveChild.bind(this)],
            css: [this.onCSS.bind(this)],
            attr: [this.onAttr.bind(this)]
        };

        console.log("[" + this.id + "] constructed!");
    }

    /**
     * This runs during the constructor or when the wspromise,
     * if provided, is fulfilled. Informs the server that this
     * widget is ready.
     */
    onCommReady() {
        APP.send({id: this.id, event: "started"});
    }

    /**
     *
     * @param {Event} event
     * @param {{}} message
     */
    onMessage(event, message) {
        console.log("[" + this.id + "] .onMessage()", message);

        // Do not bubble up to parents in the DOM.
        event.stopPropagation();

        try {
            for(let handler of this.msgHandlers[message.event]) {
                handler(message);
            }
        }
        catch (e) {
            if(!(message.event in this.msgHandlers)) {
                throw TypeError('No handler for event "' + message.event +
                    '" in this widget: ' + this.id);
            }
            else {
                throw e;
            }
        }
    }

    /**
     * Appends children sent from the server.
     * @param {{}} message
     */
    onChildren(message) {
        console.log("[" + this.id + "] .onChildren()");
        this.node.empty();
        for (let child of message.children) {
            $(child).appendTo(this.node);
        }
    }

    /**
     * Appends one child sent from the server.
     * @param {{}} message
     */
    onAppendChild(message) {
        console.log("[" + this.id + "] .onAppendChild()");
        $(message.child).appendTo(this.node);
    }

    /**
     * Removes this widget.
     * @param message
     */
    onRemoveChild(message) {
        console.log("[" + this.id + "] .onRemoveChild()");
        $("#_" + message.childid).remove();
    }

    onCSS(message) {
        console.log("[" + this.id + "] .onCSS(): ", message.css);
        this.node.css(message.css);
    }

    onAttr(message) {
        console.log("[" + this.id + "] .onAttr(): ", message.attr);
        this.node.attr(message.attr);
    }

    /**
     * Set an event handler for a specific kind of message.
     *
     * @param {string} msgtype
     * @param {function} handler
     */
    onMsgType(msgtype, handler) {
        if (!(msgtype in this.msgHandlers)) {
            this.msgHandlers[msgtype] = [];
        }

        this.msgHandlers[msgtype].push(handler.bind(this));
    }

}


/*****************************************************************
 * Widgets based on Backbone.js
 *
 * How to use:
 *
 * w = Widget2("12345", ?);
 * w.setElement($(something), model_props, wspromise);
 * w.render();
 *
 *
 * Notes:
 *   w.$el is $(w.el)
 */
class Widget2 extends Backbone.View {

    constructor(id, properties={}, parent) {
        super();

        this.id = id;  // cid is part of Backbone.View... use that?

        this.model = new Backbone.Model(properties);

        // ----- New for Backbone Widget -----
        this.children = [];
        this.setElement($('<div>'));

        this.descendent_index = {};

        this._parent = null;
        this.parent = parent;

        // The callback gets bind'ed.
        this.listenTo(this.model, 'change', this.render);

        this.model.on("change",
            function(){ console.log("Changed") });

        /**
         * Event on the DOM element.
         * This is a JQuery event. To trigger do:
         * $(el).trigger("message", message);
         */
        this.$el.on("message", this.onMessage.bind(this));

        this.msgHandlers = {
            children: [this.onChildren.bind(this)],
            append: [this.onAppendChild.bind(this)],
            remove: [this.onRemoveChild.bind(this)],
            css: [this.onCSS.bind(this)],
            attr: [this.onAttr.bind(this)]
        };

        this.message({event: "started"});

        console.log("[" + this.id + "] constructed!");
    }

    set parent(parent_widget) {
        this._parent = parent_widget;
        console.log(`[${this.id}] parent set (${parent_widget.id}).`);
        // this.parent.update_descendents(this.descendent_index);
    }

    get parent() {
        return this._parent;
    }

    get template() {
        return Handlebars.compile(
            "<button>{{label}}</button>"
        );
    }

    render() {
        this.$el.html(this.template(this.model.toJSON()));
        for (let child of this.children) {
            this.$el.append(child.$el);
        }
        return this;   // Useful convention
    }

    // get tagName() { return '#w' }

    get events() {
        return {}
    }

    message(msg) {
        msg.id = this.id;
        msg.path = [];
        this.deliver(msg);
    }

    /**
     * Get the message to the server.
     *
     * @param msg
     */
    deliver(msg) {
        msg.path.unshift(this.id);  // At the beginning.

        if (this.parent === undefined || this.parent === null) {
            throw `This widget ${this.id} does not have a parent. Cannot deliver.`;
        }

        this.parent.deliver(msg);
    }

    /**
     * Got this message from the server. Get to the right child.
     *
     * @param msg
     */
    local_deliver(msg) {
        let dstid = msg.path.shift();

        if (this.id === dstid && msg.path.length === 0) {
            this.openMessage(msg);
            return;
        }

        let child = this.get_child(msg.path[0]);
        if (child != null) {
            child.local_deliver(msg);
        }
        else {
            throw `[${this.id}] No path to widget: ${msg.path.join('.')}`;
        }
    }

    /**
     * Get a child widget by id.
     *
     * @param id
     * @returns {null|*}
     */
    get_child(id) {
        for (let child of this.children) {
            if (child.id === id) {
                return child;
            }
        }
        return null;
    }

    /**
     * This runs during the constructor or when the wspromise,
     * if provided, is fulfilled. Informs the server that this
     * widget is ready.
     */
    onCommReady() {
        this.message({event: "started"});
    }

    /**
     *
     * @param {Event} event
     * @param {{}} message
     */
    onMessage(event, message) {
        console.log("[" + this.id + "] .onMessage()", message);

        // Do not bubble up to parents in the DOM.
        event.stopPropagation();

        this.openMessage(message);
    }

    openMessage(message) {
        try {
            for(let handler of this.msgHandlers[message.event]) {
                handler(message);
            }
        }
        catch (e) {
            if(!(message.event in this.msgHandlers)) {
                throw TypeError('No handler for event "' + message.event +
                    '" in this widget: ' + this.id);
            }
            else {
                throw e;
            }
        }
    }

    /**
     * Appends children sent from the server.
     * @param {{}} message
     */
    onChildren(message) {
        console.log("[" + this.id + "] .onChildren()");
        // this.node.empty();
        // for (let child of message.children) {
        //     $(child).appendTo(this.node);
        // }
        for (let child of message.children) {
            this.children.push(
                new Widget2(child.id, child.properties, this)
            );
        }
        this.render();
    }

    /**
     * Appends one child sent from the server.
     * @param {{}} message
     */
    onAppendChild(message) {
        console.log("[" + this.id + "] .onAppendChild()");
        // $(message.child).appendTo(this.node);
        this.children.push(
            new Widget2(message.child.id, message.child.properties,
            this)
        );
    }

    /**
     * Removes this widget.
     * @param message
     */
    onRemoveChild(message) {
        console.log("[" + this.id + "] .onRemoveChild()");
        // $("#_" + message.childid).remove();
        // TODO
    }

    onCSS(message) {
        console.log("[" + this.id + "] .onCSS(): ", message.css);
        // this.node.css(message.css);
        // TODO
    }

    onAttr(message) {
        console.log("[" + this.id + "] .onAttr(): ", message.attr);
        // this.node.attr(message.attr);
        // TODO
    }

    /**
     * Set an event handler for a specific kind of message.
     *
     * @param {string} msgtype
     * @param {function} handler
     */
    onMsgType(msgtype, handler) {
        if (!(msgtype in this.msgHandlers)) {
            this.msgHandlers[msgtype] = [];
        }

        this.msgHandlers[msgtype].push(handler.bind(this));
    }

}