$(function() {
    let sliders = document.querySelectorAll(".slider");
    for(let id = 1; id <= sliders.length; id++){
        let mini = $(`#mini${id}`).html()
        let maxi = $(`#maxi${id}`).html()
        let patient = $(`#patient${id}`).html()
        patient = parseFloat(patient)
        let leftLimit, rightLimit;
        leftLimit = patient-(patient/2);
        rightLimit = patient+(patient/2);
        midLimit = " ";
        if(mini == "None" && maxi == "None"){
            mini = patient-(patient/2);
            maxi = patient+(patient/2);
            $(`#bg1${id}`).width(0)
            $(`#bg2${id}`).width(`100%`)
            $(`#bg2${id}`).css('background-color', '#1760BF')
            $(`#bg3${id}`).width(0)
        }
        mini = parseFloat(mini)
        maxi = parseFloat(maxi)
        if(patient <= mini){
            leftLimit = patient;
            rightLimit = maxi;
            midLimit = mini;
            let maxDiff = (maxi - patient);
            let nonIdeal = ((mini-patient)/maxDiff)*100;
            let ideal = ((maxi - mini)/maxDiff)*100;
            $(`#bg1${id}`).width(`${nonIdeal}%`)
            $(`#bg2${id}`).width(`${ideal}%`)
            $(`#bg3${id}`).width(0)
            $(`#mid${id}`).css('padding-left', `${nonIdeal}%`)
            if(ideal === 0){
                $(`#bg1${id}`).width(0)
                $(`#bg2${id}`).width(`100%`)
                $(`#bg2${id}`).css('background-color', '#1760BF')
                $(`#bg3${id}`).width(0)
            }
        }
        if(patient >= maxi){
            leftLimit = mini;
            rightLimit = patient;
            midLimit = maxi;
            let maxDiff = (patient - mini);
            let nonIdeal = ((patient - maxi)/maxDiff)*100;
            let ideal = ((maxi - mini)/maxDiff)*100;
            $(`#bg1${id}`).width(0)
            $(`#bg2${id}`).width(`${ideal}%`)
            $(`#bg3${id}`).width(`${nonIdeal}%`)
            $(`#mid${id}`).css('padding-left', `${ideal}%`)
            if(ideal === 0){
                $(`#bg1${id}`).width(0)
                $(`#bg2${id}`).width(`100%`)
                $(`#bg2${id}`).css('background-color', '#1760BF')
                $(`#bg3${id}`).width(0)
            }
        }
        if(mini < patient && patient < maxi){
            leftLimit = mini;
            rightLimit = maxi;
            midLimit = leftLimit;
            let maxDiff = (maxi - mini);
            let ideal = ((maxi - mini)/maxDiff)*100;
            $(`#bg1${id}`).width(0)
            $(`#bg2${id}`).width(`${ideal}%`)
            $(`#bg3${id}`).width(0)
            if(ideal === 0){
                $(`#bg1${id}`).width(0)
                $(`#bg2${id}`).width(`100%`)
                $(`#bg2${id}`).css('background-color', '#1760BF')
                $(`#bg3${id}`).width(0)
            }
        }
        if(leftLimit !== patient){
            $(`#mini${id}`).html(leftLimit)
        }
        else{
            $(`#mini${id}`).html("")
        }
        if(rightLimit !== patient){
            $(`#maxi${id}`).html(rightLimit)
        }
        else{
            $(`#maxi${id}`).html("")
        }
        $(`#mid${id}`).html(midLimit)
        var handle = $(`#custom-handle${id}`);
        $(`#slider${id}` ).slider({
            value: patient,
            min:leftLimit,
            max: rightLimit,
            create: function() {
                handle.text( $(this).slider( "value" ) );
            },
        });
    }
});