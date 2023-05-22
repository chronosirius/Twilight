const BACKDROP = document.createElement('div')
BACKDROP.style.position = 'fixed'
BACKDROP.style.width = '100vw'
BACKDROP.style.height = '100vh'
BACKDROP.style.backgroundColor = 'black'
BACKDROP.style.opacity = '0.85'
BACKDROP.id = '___backdrop'
BACKDROP.style.zIndex = '1000'
BACKDROP.style.top = '0'
BACKDROP.style.left = '0'

placeholder_supports = ['text', 'search', 'url', 'tel', 'email', 'password']
requires_outer_div = ['checkbox', 'radio', 'file', 'color', 'date', 'datetime-local']

class Modal {
    constructor(custom_id = "custom_modal", header = "Modal", inputs = [], buttons = [], is_form = false, form_options = {}) {
        var self = this
        this.modal = document.createElement('div')
        this.modal.id = "_modal-" + custom_id
        this.modal.style = 'position: fixed; width: 33%; left: 33%; height: 70%; top: 15%; color: black; background-color: white; z-index: 1001; text-align: center;'
        let h = document.createElement('h1')
        h.innerHTML = header
        this.modal.appendChild(h)
        var form;
        if (is_form) {
            form = document.createElement('form')
            if (form_options.action != null && form_options.method != null) {form.setAttribute('action', form_options.action); form.setAttribute('method', form_options.method)}
            for (let attr of Object.keys((form_options.attributes != null) ? form_options.attributes : {})) {
                form.setAttribute(attr, form_options.attributes[attr])
            }
        } else {
            form = document.createElement('div')
        }
        for (let input of inputs) {
            console.log(input._element)
            if (!input._element) {
                let ip = document.createElement('input')
                ip.id = '__modal-' + custom_id + '__input-' + input.custom_id
                ip.setAttribute('name', input.name)
                ip.style = (input.style != null) ? input.style : ''
                ip.setAttribute('type', (input.type != null) ? input.type : 'text');
                input.type = ip.getAttribute('type')
                ip.setAttribute('value', (input.prefilled != null) ? input.prefilled : "")
                for (let attribute of Object.keys((input.attributes != null) ? input.attributes:{})) {
                    ip.setAttribute(attribute, input.attributes[attribute])
                }
                if (placeholder_supports.includes(input.type)) {
                    ip.setAttribute('placeholder', (input.placeholder != null) ? input.placeholder: '')
                    form.appendChild(ip)
                } else if ((requires_outer_div.includes(input.type))) {
                    let e = document.createElement('div')
                    e.style.marginLeft = '16.5%'
                    ip.style.width = 'min-content'
                    e.appendChild(ip)
                    form.appendChild(e)
                } else {
                    form.appendChild(ip)
                }
            } else {
                let ip = input._element.cloneNode(true)
                ip.id = '__modal-' + custom_id + '__input-' + ip.id
                form.appendChild(ip)
            }
        }
        form.appendChild(document.createElement('br'))
        form.appendChild(document.createElement('br'))
        for (let button of buttons) {
            if (button._element == null) {
                let ip = document.createElement('button')
                ip.setAttribute('type', (button.type != null) ? button.type : 'button')
                ip.id = '__modal-' + custom_id + '__button-' + button.custom_id
                ip.innerHTML = button.text;
                ip.style = (button.style != null) ? button.style : ""
                for (attribute of Object.keys((button.attributes != null) ? button.attributes:{})) {
                    ip.setAttribute(attribute, button.attributes[attribute])
                }
                ip.onclick = function(ev) {
                    button.callback({
                        event: ev,
                        modal: self
                    })
                }
                form.appendChild(ip)
            } else {
                let ip = input._element.cloneNode(true)
                ip.id = '__modal-' + custom_id + '__button-' + ip.id
                ip.onclick = function(ev) {
                    button.callback({
                        event: ev,
                        modal: self
                    })
                }
            }
        }

        if (is_form) {
            let reset = document.createElement('input')
            reset.setAttribute('type', 'reset')
            reset.innerHTML = 'Reset'
            reset.style.position = 'absolute'
            reset.style.bottom = '0'
            reset.style.right = '0'
            form.appendChild(reset)
            let submit = document.createElement('input')
            submit.setAttribute('type', 'submit')
            submit.style.position = 'absolute'
            submit.style.bottom = '0'
            submit.style.left = '0'
            form.appendChild(submit)
        }

        let close = document.createElement('button')
        close.innerHTML = 'X'
        close.style.position = 'absolute'
        close.style.top = '0'
        close.style.right = '0'
        close.onclick = () => {
            self.close()
        }
        this.modal.appendChild(close)
        this.modal.appendChild(form)
    }

    show() {
        document.body.appendChild(this.modal)
        document.body.appendChild(BACKDROP.cloneNode(true))
    }

    close() {
        document.getElementById(BACKDROP.id).remove()
        document.getElementById(this.modal.id).remove()
    }
}