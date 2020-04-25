try{
    document.getElementById("follow").addEventListener("click", toggleFollow)
}
catch(e){

}

function toggleFollow(e){
    
    target = e.target
    id = target.getAttribute("data-userid")

    if(target.getAttribute("data-buttonWork")=="follow"){
        fetch('/follow/'+id)
        .then(res=>{
            if(res.status == 200){
                target.setAttribute("class", "btn btn-dark")
                target.setAttribute("data-buttonWork", "unfollow")
                target.innerText = "Unfollow"
                target.blur()
                return res.json()
            }            
        })
        .then(res=>{
            document.getElementById(id).innerText = res['followers_count']
        }) 
    }
    
    if(target.getAttribute("data-buttonWork")=="unfollow"){
        fetch('/unfollow/'+id)
        .then(res=>{
            if(res.status == 200){
                target.setAttribute("class", "btn btn-outline-primary")
                target.setAttribute("data-buttonWork", "follow")
                target.innerText = "Follow"
                target.blur()
                return res.json()
            }
        })
        .then(res=>{
            document.getElementById(id).innerText = res['followers_count']
        })
    }
}