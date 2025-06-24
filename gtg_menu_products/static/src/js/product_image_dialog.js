/** @odoo-module **/

import { Component, onMounted, useRef } from "@odoo/owl";

export class ProductImageDialog extends Component {
    static template = "custom_products_menu.ProductImageDialog";
    static props = { node: Object };

    setup() {
        this.cardRoot = useRef("cardRoot");

        onMounted(() => {
             if (this.props.node && this.cardRoot.el) {
                    const clone = this.props.node.cloneNode(true);
                    const img = clone.querySelector("img");

                    if (img) {
                        img.classList.add("custom-popup-image");
                    }

                    this.cardRoot.el.appendChild(clone);
                }
        });
    }
}
