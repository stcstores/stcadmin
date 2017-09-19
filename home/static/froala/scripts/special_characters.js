/*!
 * froala_editor v2.6.5 (https://www.froala.com/wysiwyg-editor)
 * License https://froala.com/wysiwyg-editor/terms/
 * Copyright 2014-2017 Froala Labs
 */

! function(a) {
    "function" == typeof define && define.amd ? define(["jquery"], a) : "object" == typeof module && module.exports ? module.exports = function(b, c) {
        return void 0 === c && (c = "undefined" != typeof window ? require("jquery") : require("jquery")(b)), a(c)
    } : a(window.jQuery)
}(function(a) {
    a.extend(a.FE.DEFAULTS, {
        specialCharactersSets: [
            {
            title:'Symbols',
            list: [
                {char: "&copy;", desc: "COPYRIGHT SIGN"},
                {char: "&trade;", desc: "TRADEMARK SIGN"},
                {char: "&reg;", desc: "REGISTERED SIGN"},
                {char: "&deg;", desc: "DEGREE SIGN"},
                {char: "&divide;", desc: "DIVISION SIGN"},
                {char: "&times;", desc: "MULTIPLICATION SIGN"},
                {char: "&brvbar;", desc: "BROKEN BAR"},
                {char: "&sect;", desc: "SECTION SIGN"},
                {char: "&uml;", desc: "DIAERESIS"},
                {char: "&ordf;", desc: "FEMININE ORDINAL INDICATOR"},
                {char: "&laquo;", desc: "LEFT-POINTING DOUBLE ANGLE QUOTATION MARK"},
                {char: "&not;", desc: "NOT SIGN"},
                {char: "&macr;", desc: "MACRON"},
                {char: "&plusmn;", desc: "PLUS-MINUS SIGN"},
                {char: "&sup2;", desc: "SUPERSCRIPT TWO"},
                {char: "&sup3;", desc: "SUPERSCRIPT THREE"},
                {char: "&acute;", desc: "ACUTE ACCENT"},
                {char: "&micro;", desc: "MICRO SIGN"},
                {char: "&para;", desc: "PILCROW SIGN"},
                {char: "&middot;", desc: "MIDDLE DOT"},
                {char: "&cedil;", desc: "CEDILLA"},
                {char: "&ordm;", desc: "MASCULINE ORDINAL INDICATOR"},
                {char: "&raquo;", desc: "RIGHT-POINTING DOUBLE ANGLE QUOTATION MARK"},
                {char: "&frac14;", desc: "VULGAR FRACTION ONE QUARTER"},
                {char: "&frac12;", desc: "VULGAR FRACTION ONE HALF"},
                {char: "&frac34;", desc: "VULGAR FRACTION THREE QUARTERS"},
                {char: "&iexcl;", desc: "INVERTED EXCLAMATION MARK"},
                {char: "&iquest;", desc: "INVERTED QUESTION MARK"},
            ]
        }, {
            title: "Currency",
            list: [
                {char: "&pound;", desc: "POUND SIGN"},
                {char: "&#x20AC", desc: "EURO SIGN"},
                {char: "&cent;", desc: "CENT SIGN"},
                {char: "&#x20A3", desc: "FRENCH FRANC SIGN"},
                {char: "&#x20B0", desc: "GERMAN PENNY SYMBOL"},
                {char: "&#x20A4", desc: "LIRA SIGN"},
                {char: "&yen;", desc: "YEN SIGN"},
                {char: "&#x20A7", desc: "PESETA SIGN"},
                {char: "&#x20B1",desc: "PESO SIGN"},
                {char: "&curren;", desc: "CURRENCY SIGN"},
                {char: "&#x20AB", desc: "DONG SIGN"},
                {char: "&#x20A1", desc: "COLON SIGN"}]
            }, {
            title: "Punctuation",
            list: [
                {char: "&ndash;", desc: "EN DASH"},
                {char: "&mdash;", desc: "EM DASH"},
                {char: "&lsquo;", desc: "LEFT SINGLE QUOTATION MARK"},
                {char: "&rsquo;", desc: "RIGHT SINGLE QUOTATION MARK"},
                {char: "&sbquo;", desc: "SINGLE LOW-9 QUOTATION MARK"},
                {char: "&ldquo;", desc: "LEFT DOUBLE QUOTATION MARK"},
                {char: "&rdquo;", desc: "RIGHT DOUBLE QUOTATION MARK"},
                {char: "&bdquo;", desc: "DOUBLE LOW-9 QUOTATION MARK"},
                {char: "&dagger;", desc: "DAGGER"},
                {char: "&Dagger;", desc: "DOUBLE DAGGER"},
                {char: "&bull;", desc: "BULLET"},
                {char: "&hellip;", desc: "HORIZONTAL ELLIPSIS"},
                {char: "&permil;", desc: "PER MILLE SIGN"},
                {char: "&prime;", desc: "PRIME"},
                {char: "&Prime;", desc: "DOUBLE PRIME"},
                {char: "&lsaquo;", desc: "SINGLE LEFT-POINTING ANGLE QUOTATION MARK"},
                {char: "&rsaquo;", desc: "SINGLE RIGHT-POINTING ANGLE QUOTATION MARK"},
                {char: "&oline;", desc: "OVERLINE"},
                {char: "&frasl;", desc: "FRACTION SLASH"}]
        }, {
            title: "Latin",
            list: [
                {char: "&Agrave;", desc: "LATIN CAPITAL LETTER A WITH GRAVE"},
                {char: "&Aacute;",desc: "LATIN CAPITAL LETTER A WITH ACUTE"},
                {char: "&Acirc;", desc: "LATIN CAPITAL LETTER A WITH CIRCUMFLEX"},
                {char: "&Atilde;", desc: "LATIN CAPITAL LETTER A WITH TILDE"},
                {char: "&Auml;", desc: "LATIN CAPITAL LETTER A WITH DIAERESIS "},
                {char: "&Aring;", desc: "LATIN CAPITAL LETTER A WITH RING ABOVE"},
                {char: "&AElig;", desc: "LATIN CAPITAL AE LIGATURE"},
                {char: "&Ccedil;", desc: "LATIN CAPITAL LETTER C WITH CEDILLA"},
                {char: "&Egrave;", desc: "LATIN CAPITAL LETTER E WITH GRAVE"},
                {char: "&Eacute;", desc: "LATIN CAPITAL LETTER E WITH ACUTE"},
                {char: "&Ecirc;", desc: "LATIN CAPITAL LETTER E WITH CIRCUMFLEX"},
                {char: "&Euml;", desc: "LATIN CAPITAL LETTER E WITH DIAERESIS"},
                {char: "&Igrave;", desc: "LATIN CAPITAL LETTER I WITH GRAVE"},
                {char: "&Iacute;", desc: "LATIN CAPITAL LETTER I WITH ACUTE"},
                {char: "&Icirc;", desc: "LATIN CAPITAL LETTER I WITH CIRCUMFLEX"},
                {char: "&Iuml;", desc: "LATIN CAPITAL LETTER I WITH DIAERESIS"},
                {char: "&ETH;", desc: "LATIN CAPITAL LETTER ETH"},
                {char: "&Ntilde;", desc: "LATIN CAPITAL LETTER N WITH TILDE"},
                {char: "&Ograve;", desc: "LATIN CAPITAL LETTER O WITH GRAVE"},
                {char: "&Oacute;", desc: "LATIN CAPITAL LETTER O WITH ACUTE"},
                {char: "&Ocirc;", desc: "LATIN CAPITAL LETTER O WITH CIRCUMFLEX"},
                {char: "&Otilde;", desc: "LATIN CAPITAL LETTER O WITH TILDE"},
                {char: "&Ouml;", desc: "LATIN CAPITAL LETTER O WITH DIAERESIS"},
                {char: "&Oslash;", desc: "LATIN CAPITAL LETTER O WITH STROKE"},
                {char: "&Ugrave;", desc: "LATIN CAPITAL LETTER U WITH GRAVE"},
                {char: "&Uacute;", desc: "LATIN CAPITAL LETTER U WITH ACUTE"},
                {char: "&Ucirc;", desc: "LATIN CAPITAL LETTER U WITH CIRCUMFLEX"},
                {char: "&Uuml;", desc: "LATIN CAPITAL LETTER U WITH DIAERESIS"},
                {char: "&Yacute;", desc: "LATIN CAPITAL LETTER Y WITH ACUTE"},
                {char: "&THORN;", desc: "LATIN CAPITAL LETTER THORN"},
                {char: "&szlig;", desc: "LATIN SMALL LETTER SHARP S"},
                {char: "&agrave;", desc: "LATIN SMALL LETTER A WITH GRAVE"},
                {char: "&aacute;", desc: "LATIN SMALL LETTER A WITH ACUTE "},
                {char: "&acirc;", desc: "LATIN SMALL LETTER A WITH CIRCUMFLEX"},
                {char: "&atilde;", desc: "LATIN SMALL LETTER A WITH TILDE"},
                {char: "&auml;", desc: "LATIN SMALL LETTER A WITH DIAERESIS"},
                {char: "&aring;", desc: "LATIN SMALL LETTER A WITH RING ABOVE"},
                {char: "&aelig;",desc: "LATIN SMALL AE LIGATURE"},
                {char: "&ccedil;", desc: "LATIN SMALL LETTER C WITH CEDILLA"},
                {char: "&egrave;", desc: "LATIN SMALL LETTER E WITH GRAVE"},
                {char: "&eacute;", desc: "LATIN SMALL LETTER E WITH ACUTE"},
                {char: "&ecirc;", desc: "LATIN SMALL LETTER E WITH CIRCUMFLEX"},
                {char: "&euml;", desc: "LATIN SMALL LETTER E WITH DIAERESIS"},
                {char: "&igrave;", desc: "LATIN SMALL LETTER I WITH GRAVE"},
                {char: "&iacute;", desc: "LATIN SMALL LETTER I WITH ACUTE"},
                {char: "&icirc;", desc: "LATIN SMALL LETTER I WITH CIRCUMFLEX"},
                {char: "&iuml;", desc: "LATIN SMALL LETTER I WITH DIAERESIS"},
                {char: "&eth;", desc: "LATIN SMALL LETTER ETH"},
                {char: "&ntilde;", desc: "LATIN SMALL LETTER N WITH TILDE"},
                {char: "&ograve;", desc: "LATIN SMALL LETTER O WITH GRAVE"},
                {char: "&oacute;",desc: "LATIN SMALL LETTER O WITH ACUTE"},
                {char: "&ocirc;", desc: "LATIN SMALL LETTER O WITH CIRCUMFLEX"},
                {char: "&otilde;", desc: "LATIN SMALL LETTER O WITH TILDE"},
                {char: "&ouml;", desc: "LATIN SMALL LETTER O WITH DIAERESIS"},
                {char: "&oslash;", desc: "LATIN SMALL LETTER O WITH STROKE"},
                {char: "&ugrave;", desc: "LATIN SMALL LETTER U WITH GRAVE"},
                {char: "&uacute;", desc: "LATIN SMALL LETTER U WITH ACUTE"},
                {char: "&ucirc;", desc: "LATIN SMALL LETTER U WITH CIRCUMFLEX"},
                {char: "&uuml;", desc: "LATIN SMALL LETTER U WITH DIAERESIS"},
                {char: "&yacute;", desc: "LATIN SMALL LETTER Y WITH ACUTE"},
                {char: "&thorn;", desc: "LATIN SMALL LETTER THORN"},
                {char: "&yuml;", desc: "LATIN SMALL LETTER Y WITH DIAERESIS"}]
        }, {
            title: "Greek",
            list: [
                {char: "&Alpha;", desc: "GREEK CAPITAL LETTER ALPHA"},
                {char: "&Beta;", desc: "GREEK CAPITAL LETTER BETA"},
                {char: "&Gamma;", desc: "GREEK CAPITAL LETTER GAMMA"},
                {char: "&Delta;", desc: "GREEK CAPITAL LETTER DELTA"},
                {char: "&Epsilon;", desc: "GREEK CAPITAL LETTER EPSILON"},
                {char: "&Zeta;", desc: "GREEK CAPITAL LETTER ZETA"},
                {char: "&Eta;", desc: "GREEK CAPITAL LETTER ETA"},
                {char: "&Theta;", desc: "GREEK CAPITAL LETTER THETA"},
                {char: "&Iota;", desc: "GREEK CAPITAL LETTER IOTA"},
                {char: "&Kappa;", desc: "GREEK CAPITAL LETTER KAPPA"},
                {char: "&Lambda;", desc: "GREEK CAPITAL LETTER LAMBDA"},
                {char: "&Mu;", desc: "GREEK CAPITAL LETTER MU"},
                {char: "&Nu;", desc: "GREEK CAPITAL LETTER NU"},
                {char: "&Xi;", desc: "GREEK CAPITAL LETTER XI"},
                {char: "&Omicron;", desc: "GREEK CAPITAL LETTER OMICRON"},
                {char: "&Pi;", desc: "GREEK CAPITAL LETTER PI" },
                {char: "&Rho;", desc: "GREEK CAPITAL LETTER RHO"},
                {char: "&Sigma;", desc: "GREEK CAPITAL LETTER SIGMA"},
                {char: "&Tau;", desc: "GREEK CAPITAL LETTER TAU"},
                {char: "&Upsilon;", desc: "GREEK CAPITAL LETTER UPSILON"},
                {char: "&Phi;", desc: "GREEK CAPITAL LETTER PHI"},
                {char: "&Chi;", desc: "GREEK CAPITAL LETTER CHI"},
                {char: "&Psi;", desc: "GREEK CAPITAL LETTER PSI"},
                {char: "&Omega;", desc: "GREEK CAPITAL LETTER OMEGA"},
                {char: "&alpha;", desc: "GREEK SMALL LETTER ALPHA"},
                {char: "&beta;", desc: "GREEK SMALL LETTER BETA"},
                {char: "&gamma;", desc: "GREEK SMALL LETTER GAMMA"},
                {char: "&delta;", desc: "GREEK SMALL LETTER DELTA"},
                {char: "&epsilon;", desc: "GREEK SMALL LETTER EPSILON"},
                {char: "&zeta;", desc: "GREEK SMALL LETTER ZETA"},
                {char: "&eta;", desc: "GREEK SMALL LETTER ETA"},
                {char: "&theta;", desc: "GREEK SMALL LETTER THETA"},
                {char: "&iota;", desc: "GREEK SMALL LETTER IOTA"},
                {char: "&kappa;", desc: "GREEK SMALL LETTER KAPPA"},
                {char: "&lambda;", desc: "GREEK SMALL LETTER LAMBDA"},
                {char: "&mu;", desc: "GREEK SMALL LETTER MU"},
                {char: "&nu;", desc: "GREEK SMALL LETTER NU"},
                {char: "&xi;", desc: "GREEK SMALL LETTER XI"},
                {char: "&omicron;", desc: "GREEK SMALL LETTER OMICRON"},
                {char: "&pi;", desc: "GREEK SMALL LETTER PI"},
                {char: "&rho;", desc: "GREEK SMALL LETTER RHO"},
                {char: "&sigmaf;", desc: "GREEK SMALL LETTER FINAL SIGMA"},
                {char: "&sigma;", desc: "GREEK SMALL LETTER SIGMA"},
                {char: "&tau;", desc: "GREEK SMALL LETTER TAU"},
                {char: "&upsilon;", desc: "GREEK SMALL LETTER UPSILON"},
                {char: "&phi;", desc: "GREEK SMALL LETTER PHI"},
                {char: "&chi;", desc: "GREEK SMALL LETTER CHI"},
                {char: "&psi;", desc: "GREEK SMALL LETTER PSI"},
                {char: "&omega;", desc: "GREEK SMALL LETTER OMEGA"},
                {char: "&thetasym;", desc: "GREEK THETA SYMBOL"},
                {char: "&upsih;", desc: "GREEK UPSILON WITH HOOK SYMBOL"},
                {char: "&straightphi;", desc: "GREEK PHI SYMBOL"},
                {char: "&piv;", desc: "GREEK PI SYMBOL"},
                {char: "&Gammad;", desc: "GREEK LETTER DIGAMMA"},
                {char: "&gammad;", desc: "GREEK SMALL LETTER DIGAMMA"},
                {char: "&varkappa;", desc: "GREEK KAPPA SYMBOL"},
                {char: "&varrho;", desc: "GREEK RHO SYMBOL"},
                {char: "&straightepsilon;", desc: "GREEK LUNATE EPSILON SYMBOL"},
                {char: "&backepsilon;", desc: "GREEK REVERSED LUNATE EPSILON SYMBOL"}]
        }]
    }), a.FE.PLUGINS.specialCharacters = function(b) {
        function c() {}

        function d() {
            for (var c = '<div class="fr-special-characters-modal">', d = 0; d < a.FE.DEFAULTS.specialCharactersSets.length; d++) {
                for (var e = a.FE.DEFAULTS.specialCharactersSets[d], f = e.list, g = '<div class="fr-special-characters-list"><p class="fr-special-characters-title">' + e.title + "</p>", h = 0; h < f.length; h++) {
                    var i = f[h];
                    g += '<span class="fr-command fr-special-character" tabIndex="-1" role="button" value="' + i.char + '" title="' + i.desc + '">' + i.char + '<span class="fr-sr-only">' + b.language.translate(i.desc) + "&nbsp;&nbsp;&nbsp;</span></span>"
                }
                c += g + "</div>"
            }
            return c += "</div>"
        }

        function e(a, c) {
            b.events.disableBlur(), a.focus(), c.preventDefault(), c.stopPropagation()
        }

        function f() {
            b.events.$on(l, "keydown", function(c) {
                var d = c.which,
                    f = l.find("span.fr-special-character:focus:first");
                if (!(f.length || d != a.FE.KEYCODE.F10 || b.keys.ctrlKey(c) || c.shiftKey) && c.altKey) {
                    var g = l.find("span.fr-special-character:first");
                    return e(g, c), !1
                }
                if (d == a.FE.KEYCODE.TAB || d == a.FE.KEYCODE.ARROW_LEFT || d == a.FE.KEYCODE.ARROW_RIGHT) {
                    var h = null,
                        i = null,
                        k = !1;
                    return d == a.FE.KEYCODE.ARROW_LEFT || d == a.FE.KEYCODE.ARROW_RIGHT ? (i = d == a.FE.KEYCODE.ARROW_RIGHT, k = !0) : i = !c.shiftKey, f.length ? (k && (h = i ? f.nextAll("span.fr-special-character:first") : f.prevAll("span.fr-special-character:first")), h && h.length || (h = i ? f.parent().next().find("span.fr-special-character:first") : f.parent().prev().find("span.fr-special-character:" + (k ? "last" : "first")), h.length || (h = l.find("span.fr-special-character:" + (i ? "first" : "last"))))) : h = l.find("span.fr-special-character:" + (i ? "first" : "last")), e(h, c), !1
                }
                if (d != a.FE.KEYCODE.ENTER || !f.length) return !0;
                var m = j.data("instance") || b;
                m.specialCharacters.insert(f)
            }, !0)
        }

        function g() {
            if (!j) {
                var c = "<h4>Special Characters</h4>",
                    e = d(),
                    g = b.modals.create(m, c, e);
                j = g.$modal, k = g.$head, l = g.$body, b.events.$on(a(b.o_win), "resize", function() {
                    var a = j.data("instance") || b;
                    a.modals.resize(m)
                }), b.events.bindClick(l, ".fr-special-character", function(c) {
                    var d = j.data("instance") || b,
                        e = a(c.currentTarget);
                    d.specialCharacters.insert(e)
                }), f()
            }
            b.modals.show(m), b.modals.resize(m)
        }

        function h() {
            b.modals.hide(m)
        }

        function i(a) {
            b.specialCharacters.hide(), b.undo.saveStep(), b.html.insert(a.attr("value"), !0), b.undo.saveStep()
        }
        var j, k, l, m = "special_characters";
        return {
            _init: c,
            show: g,
            hide: h,
            insert: i
        }
    }, a.FroalaEditor.DefineIcon("specialCharacters", {
        template: "text",
        NAME: "&#937;"
    }), a.FE.RegisterCommand("specialCharacters", {
        title: "Special Characters",
        icon: "specialCharacters",
        undo: !1,
        focus: !1,
        modal: !0,
        callback: function() {
            this.specialCharacters.show()
        },
        plugin: "specialCharacters",
        showOnMobile: !1
    })
});
