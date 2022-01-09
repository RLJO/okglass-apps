odoo.define('ecommerce_custom.custom', function (require) {
'use strict';
    var ajax= require('web.ajax')

    jQuery(document).ready(function(){

        jQuery("#carousel-custom").owlCarousel({
          autoplay: true,
          rewind: true,
          margin: 5,
          responsiveClass: true,
          autoHeight: true,
          autoplayTimeout: 3000,
          smartSpeed: 800,
          nav: true,
          responsive: {
            0: {
              items: 1
            },

            600: {
              items: 1
            },

            1024: {
              items: 1
            },

            1366: {
              items: 1
            }
          }
       });

    });
});
