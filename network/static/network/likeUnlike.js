function getEventTarget(e){
    e = e || window.event
    return e.target || e.srcElement;
}

function clickHandler(e){
    target = getEventTarget(e)            
    if(target.tagName.toLowerCase()=="i"){
        id = target.getAttribute("data-buttonid");
        likeCount = document.getElementById(id);
        if(target.getAttribute("data-buttonWork")=="like"){
            fetch('/like/'+id)
            .then(res=>{
                if(res.status == 200){
                    target.setAttribute("class", "fa fa-thumbs-up text-primary")      
                    target.setAttribute("data-buttonWork", "unlike")  
                    return res.json()
                }                
            })
            .then(res=>{
                likeCount.innerText = res['likes_count']
            })
        }
        
        if(target.getAttribute("data-buttonWork")=="unlike"){
            fetch('/unlike/'+id)
            .then(res=>{
                if(res.status == 200){
                    target.setAttribute("class", "far fa-thumbs-up text-secondary")
                    target.setAttribute("data-buttonWork", "like")  
                    return res.json()  
                }
            })
            .then(res=>{
                likeCount.innerText = res['likes_count']
            })
        }
    }
}