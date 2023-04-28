// https://github.com/chronosirius/ctxmenu-client/blob/main/ctxmenu.js

window.addEventListener('load', function() {
    document.body.addEventListener('contextmenu', function(ev) {
        el = document.getElementById('_ctxmenu_element')
        if (el != null) {
            ev.preventDefault()
            el.remove()
        }
    })
})

class ContextMenuContext {
    constructor(event, button, menu, ctx_menu_manager, query, element) {
        this.event = event;
        this.button = button;
        this.menu_element = menu;
        this.ctxmenu_manager = ctx_menu_manager;
        this.target = event.target;
        this.query = query;
        this.element = element;
    }
}

class CtxMenu {
    constructor(contextmenu_frame) {
        var menu = document.createElement('div')
        menu.style.position = 'fixed'
        menu.style.background = 'var(--ctxmenu-bg-color)'
        menu.id = '_ctxmenu_element'
        this.registrations = [];
        for (let custmenu of contextmenu_frame) {
            let btn = document.createElement('button')
            btn.appendChild(document.createTextNode(custmenu.text))
            btn.style.color = (custmenu.color != null) ? custmenu.color : 'var(--ctxmenu-text-color)'
			btn.style.background = (custmenu.bg != null) ? custmenu.bg : 'var(--ctxmenu-btn-bg-color)'
            btn.style.borderWidth = '1.5px'
			btn.style.width = '120px'
            btn.addEventListener('contextmenu', (ev) => {ev.preventDefault()})
            let callback = custmenu.callback
            btn._fire_handler = function(context) {
                document.getElementById('_ctxmenu_element').remove()
                callback(context)
            }
            menu.appendChild(btn)
            if (--contextmenu_frame.length) {
                menu.appendChild(document.createElement('br'))
            }
        }
        this.menu = menu
    }

    register(query) {
        var self = this
        Array.from(document.querySelectorAll(query)).forEach(function(queried_element) {
            if (!self.registrations.includes(queried_element)) {
                queried_element.addEventListener('contextmenu', function(ev) {
                    ev.preventDefault()
                    ev.stopPropagation()
                    if (document.getElementById('_ctxmenu_element') == null) {
                        let cm = self.menu.cloneNode(false)
                        cm.addEventListener('contextmenu', (ev) => {ev.preventDefault()})
                        cm.style.top = `${ev.pageY}px`
                        cm.style.left = `${ev.pageX}px`
                        cm.style.height = 'fit-content'
                        for (let buttonnum = 0; buttonnum < self.menu.children.length; buttonnum++) {
                            let button = self.menu.children[buttonnum].cloneNode(true)
                            button._fire_handler = self.menu.children[buttonnum]._fire_handler
                            let event_context_uf = new ContextMenuContext(ev, button, cm, self, query, queried_element)
                            button.addEventListener('contextmenu', (ev) => {ev.preventDefault()})
                            button.onclick = function() {
                                button._fire_handler(event_context_uf)
                            }
                            cm.appendChild(button)
                        }
                        document.body.appendChild(cm)
                    } else {
                        document.getElementById('_ctxmenu_element').remove()
                    }
                })
                self.registrations.push(queried_element)
                document.addEventListener('click', function(e) {
                    if (document.getElementById('_ctxmenu_element') != null) {
                        if (e.target.offsetParent != document.getElementById('_ctxmenu_element')) {
                            document.getElementById('_ctxmenu_element').remove()
                        }
                    }
                })
            }
        })
    }
}