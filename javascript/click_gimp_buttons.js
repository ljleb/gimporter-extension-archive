function click_gimp_refresh_buttons() {
    ['img2img_image', 'img2maskimg', 'img_inpaint_base', 'img_inpaint_mask'].forEach(elem_id => {
        gradioApp().querySelector(`#gimp_refresh_${elem_id}`).click();
    })
}

setInterval(click_gimp_refresh_buttons, 3000);