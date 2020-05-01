function getEventTarget(e){
    e = e || window.event
    return e.target || e.srcElement;
}

function clickHandler(e){
    target = getEventTarget(e)    

    if(target.tagName.toLowerCase()=="i" && target.className.includes("thumbs")){
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

    //editButton Click
    if(target.tagName.toLowerCase()=="i" && target.className.includes("edit")){    
        parent = e.target.parentNode
        postTextDiv = parent.querySelector("div.post-text")

        //get Text to write in textarea
        postText = postTextDiv.innerText.replace(/\n/g, '<br>')

        //make editable with editable Div
        postTextDiv.innerHTML = "<div class='input editarea' role='textBox' contenteditable >" + postText + "</div>"
        postTextDiv.childNodes[0].focus()

        target.style.display= "none"
       
        //show save button
        saveButton = parent.querySelector("button")
        saveButton.style.display = "block"
    }

    //save Edited
    if(target.tagName.toLowerCase()=="button" && target.className.includes("save-btn")){        
        id = target.getAttribute("data-id");
        parent = e.target.parentNode
        postTextDiv = parent.querySelector("div.input.editarea")
        postText = postTextDiv.innerText
        csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        fetch('/edit_post/'+id, {
            method: 'POST',
            headers: {'X-CSRFToken': csrftoken},
            body: JSON.stringify({"post_text": postText}),
          })
        .then(res =>{
            if(res.status==200){
                return res.json()
            }
            return "Failed"
            
        })
        .then(res=>{
            try{
                postText = res['edited_post']
            }            
            catch{
                true;
            }
            parent = e.target.parentNode
            postTextDiv = parent.querySelector("div.post-text")
            postTextDiv.innerHTML = postText.replace(/\n/g, '<br>')
            target.style.display = "none"
            parent.querySelector("i.far.fa-edit.text-secondary").style.display = "inline-block"
        })
        .catch(error=>console.log(error))
    }

}
