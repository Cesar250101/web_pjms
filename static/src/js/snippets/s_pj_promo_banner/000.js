/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

const AUTOPLAY_INTERVAL = 6000;

publicWidget.registry.sPjPromoBanner = publicWidget.Widget.extend({
    selector: ".s_pj_promo_banner",
    events: {
        "click [data-promo-prev]": "_onPrev",
        "click [data-promo-next]": "_onNext",
        "click [data-promo-dot]": "_onDot",
    },

    start() {
        this._current = 0;
        this._slides = this.el.querySelectorAll(".pj-promo-slide");
        this._dots = this.el.querySelectorAll(".pj-promo-dot");
        this._total = this._slides.length;
        if (this._total > 1) {
            this._startAutoplay();
        }
        return this._super(...arguments);
    },

    destroy() {
        this._stopAutoplay();
        this._super(...arguments);
    },

    _goTo(index) {
        if (this._total <= 1) return;
        this._slides[this._current].classList.remove("active");
        if (this._dots[this._current]) this._dots[this._current].classList.remove("active");
        this._current = (index + this._total) % this._total;
        this._slides[this._current].classList.add("active");
        if (this._dots[this._current]) this._dots[this._current].classList.add("active");
    },

    _onPrev(ev) {
        ev.preventDefault();
        this._stopAutoplay();
        this._goTo(this._current - 1);
        this._startAutoplay();
    },
    _onNext(ev) {
        ev.preventDefault();
        this._stopAutoplay();
        this._goTo(this._current + 1);
        this._startAutoplay();
    },
    _onDot(ev) {
        ev.preventDefault();
        const index = parseInt(ev.currentTarget.dataset.promoDot, 10);
        this._stopAutoplay();
        this._goTo(index);
        this._startAutoplay();
    },

    _startAutoplay() {
        this._stopAutoplay();
        this._timer = setInterval(() => this._goTo(this._current + 1), AUTOPLAY_INTERVAL);
    },
    _stopAutoplay() {
        if (this._timer) { clearInterval(this._timer); this._timer = null; }
    },
});

export default publicWidget.registry.sPjPromoBanner;
