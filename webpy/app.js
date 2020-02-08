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

        // Runs when the WebSocket connects. Resolves the wsopen
        // promise/deferred.
        this.ws.onopen = function() {
            console.log("[APP] Websocket connection ready.");
            this.topwidget = new Widget2("topwidget", {}, this, {className: "widget"});
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
    },

    /**
     * Sends a message to the server.
     * @param message
     */
    send: function(message) {
        this.ws.send(JSON.stringify(message));
    },

    deliver: function(message) {
        this.send(message);
    },

    setup: function() {
        Handlebars.registerHelper('if_eq', function(a, b, opts) {
            if (a === b) {
                return opts.fn(this);
            } else {
                return opts.inverse(this);
            }
        });
    },

    outbox: []

};


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

    constructor(id, properties={}, parent,
                {
                    attributes={},
                    style={},
                    tagName="div",
                    className="widget",
                    template="",
                    renderOnChange=true,
                    notifyServerOnChange=true
                } = {}) {

        super({
            className: className,
            tagName: tagName
        });

        this.id = id;  // cid is part of Backbone.View... use that?
        console.log(`[${this.id}] constructor()`);

        this.model = new Backbone.Model(properties);

        // ----- New for Backbone Widget -----
        this.children = [];
        // this.className = cssclass;
        // this.setElement($(`<${tag}>`));
        this.$el.attr(attributes);
        this.$el.css(style);

        this.descendent_index = {};

        this._parent = null;
        this.parent = parent;

        this.template_src = template;

        // The callback gets bind'ed with this.listenTo.
        if (renderOnChange) {
            this.listenTo(this.model, 'change', this.render);
        }

        if (notifyServerOnChange) {
            this.listenTo(this.model, 'change',
                function (model, options) {
                    if (options.source == "message") {
                        console.log(`[${this.id}] model data change from server.`);
                    } else {
                        console.log(`[${this.id}] model data change locally.`);
                        this.message({'event': 'change', 'properties': this.model.toJSON()});
                    }
                });

        }

        this.model.on("change",
            function(){ console.log("Changed") });

        /**
         * Event on the DOM element.
         * This is a JQuery event. To trigger do:
         * $(el).trigger("message", message);
         */
        this.$el.on("message", this.onMessage.bind(this));
        // TODO: This above does not appear to be used any more.

        // Handlers per message type.
        this.msgHandlers = {
            children: [this.onChildren.bind(this)],
            append: [this.onAppendChild.bind(this)],
            remove: [this.onRemoveChild.bind(this)],
            css: [this.onCSS.bind(this)],
            attr: [this.onAttr.bind(this)],
            properties: [this.onProperties.bind(this)]
        };

        this.message({event: "started"});

        console.log("[" + this.id + "] constructed!");
    }

    initialize(options) {
        console.log(`[${this.id}] initialize()`);
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
            this.template_src
        );
    }

    render() {
        console.log(`[${this.id}] render()`);
        // TODO: Perhaps we want to render this widget after the children.
        this.$el.empty();
        this.$el.html(this.template(this.model.toJSON()));
        for (let child of this.children) {
            this.$el.append(child.$el);
            child.render();
        }
        return this;   // Useful convention
    }

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

        // Oh! It's for me!
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
        this.children = [];
        for (let child of message.children) {
            this.children.push(this.fromJSON(child));
        }
        this.render();
    }

    /**
     * Creates a Widget2 instance from its JSON representation.
     *
     * @param widgetJSON
     * @returns {Widget2}
     */
    fromJSON(widgetJSON) {
        
        let newWidget = new Widget2(
            widgetJSON.id,
            widgetJSON.properties,
            this,
            {   // TODO: Manually listing these is very error prone.
                attributes: widgetJSON.attributes,
                style: widgetJSON.style,
                tagName: widgetJSON.tagName,
                className: widgetJSON.className,
                template: widgetJSON.template,
                renderOnChange: widgetJSON.renderOnChange,
                notifyServerOnChange: widgetJSON.notifyServerOnChange
            }
        );

        // Event handlers
        // Note: It may be convenient to use the view's delegateEvents instead of
        // directly using jQuery's mechanism.

        for (let [handlerName, handlerBody] of Object.entries(widgetJSON.handlers)) {
            newWidget.$el.on(handlerName, Function('event', handlerBody).bind(newWidget));
        }

        if (widgetJSON.render !== null) {
            // this.listenTo(this.model, 'change', this.render);
            newWidget.stopListening(newWidget.model, 'change', newWidget.render);
            newWidget.render = Function(widgetJSON.render);
            newWidget.listenTo(newWidget.model, 'change', newWidget.render);
        }

        return newWidget
    }

    /**
     * Appends one child sent from the server. This is triggered when
     * a message is received from the server and msg.event == 'append'.
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
        this.$el.css(message.css);
    }

    onAttr(message) {
        console.log("[" + this.id + "] .onAttr(): ", message.attr);
        this.$el.attr(message.attr);
    }

    onProperties(message) {
        console.log("[" + this.id + "] .onProperties(): ", message.properties);

        this.model.set(message.properties, {source: 'message'});
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