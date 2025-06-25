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
        const context = this.props.record?.context || this.props.context || {};
        const isCustomPopupEnabled = context.custom_product_popup_enabled;

        if (!isCustomPopupEnabled) {
            // 👇 fallback to default click behavior
            return super.onGlobalClick(ev);
        }

        const card = ev.currentTarget;

        if (card) {
            this.dialog.closeAll();  // ✅ only one popup at a time
            this.dialog.add(ProductImageDialog, { node: card.cloneNode(true) }, {
                title: false,
                dialogClass: "bg-transparent border-0 shadow-none p-0",
            });
        }

        ev.preventDefault();
        ev.stopPropagation();
    },
});
