$(document).ready(() => {
    let cnt = 0
    gsap.utils.toArray(".index__container-parent").forEach(ele => {
        if($(ele).attr('id') == undefined) return
        let tl = gsap.timeline({
            scrollTrigger: {
                trigger: ele,
                start: 'center top',
                end: 'bottom center'
            }
        })
        let scroll = document.getElementsByClassName('index__scroll')[cnt]
        if(scroll == undefined) return
        console.log(scroll)
        tl.fromTo(scroll, 
            {
                x: "-100vw",
                scrub: true,
            },
            {
                x: 0,
                scrub: true,
            }
        )
        cnt+=1
    });
});