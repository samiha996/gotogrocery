/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { KanbanRecord } from "@web/views/kanban/kanban_record";
import { useService } from "@web/core/utils/hooks";
import { ProductImageDialog } from "./product_image_dialog";

patch(KanbanRecord.prototype, {
    setup() {
        super.setup();
        this.dialog = useService("dialog");
    },

    async onGlobalClick(ev) {
        const card = ev.currentTarget;

        if (card) {
            this.dialog.closeAll();  // remove any previous popup
            this.dialog.add(ProductImageDialog, { node: card.cloneNode(true) }, {
                title: false,
                dialogClass: "bg-transparent border-0 shadow-none p-0",
            });
        }

        ev.preventDefault();
        ev.stopPropagation();
    },
});
