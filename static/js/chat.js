//protocol = window.location.protocol; <- For determining what protocol is being used.

let socket = io.connect('https://' + document.domain + ':' + location.port);

const url = window.location.href.split('/')
const chatID = url.pop()

const scrollTop = $(document).scrollTop();

window.scrollTo(scrollTop, document.body.scrollHeight)

let page = 2;

document.addEventListener("scroll", () => window.scrollY === 0 ? loadMessages() : "")

sessionStorage.removeItem('otherUserProfilePicture')

function loadMessages(){
    
    // Sent request to server to retrieve the next 10 messages
    // prepend the next 10 messages to the message_holder.

    if (!($('.loader').length)){
        
        $('div.message_holder').prepend(
        '<div class="loader fa-3x"> <i class="fas fa-spinner fa-spin"></i> </div>')
    }

    setTimeout(ajaxForMessages, 1)

}

function ajaxForMessages(){
    $.get(`/chat/messages/${chatID}/${page}.json`, (data) => {appendPrevMessages(data)})

    page = page + 1
}

function appendPrevMessages(data){

    if (Object.keys(data).length === 2 && !($(".no-messages").length)){
        $('div.message_holder').prepend('<p class="no-messages"> No more messages </p>')
    }

        // loops through the number keys in the json object and prepends them to the page.
        for (let item of Object.keys(data)){
            if (!isNaN(parseInt(item))){
                $('div.message_holder').prepend( `<div class="row ${ data['currentUser'] == data[item][0] ? '' : 'd-flex flex-row-reverse'}"> ${data['currentUser'] == data[item][0] ? '<div class="chat-current-user-pic"></div>' : '<div class="chat-other-user-pic"></div>'}  <div class="sent-message ${ data['currentUser'] == data[item][0] ? 'current-user-sender col-md-5' : 'other-user-sender col-md-offset-5 col-md-7 '}"><b>` + data[item][1] + '</b>: ' + data[item][2] + '</div></div>')
            }
        }
    getProfileImages()

    $(".loader").remove()
}

socket.on('connect', () => {
    console.log("joined websocket")

    socket.emit('join', { room: chatID })
    })

socket.on('disconnect', () => {
console.log('DISCONNECTED')})

// Every time a user sends a message:
let form = $('form').on('submit', (e) => {
  e.preventDefault()
  let user_input = $('input.message').val()
  socket.emit('message', {
    room : chatID,
    message : user_input
  })
  $('input.message').val('').focus()
})


  socket.on('my_response', (msg) => {

    if ( typeof msg.username !== 'undefined'){
      $('div.message_holder').append( `<div class="row ${currentUser === msg.sender ? '' : 'd-flex flex-row-reverse'}"> 
                                        ${currentUser === msg.sender ? '<div class="chat-current-user-pic"></div>' : '<div class="chat-other-user-pic"></div>'}
                                        <div class="sent-message ${ currentUser === msg.sender ? 'current-user-sender col-md-5' : 'other-user-sender col-md-offset-5 col-md-7 '}"><b>` + msg.username + '</b>: ' + msg.message + '</div></div>')
    }
    if (currentUser !== msg.sender){

        fetch('/chat/messages/markread.json', {
            method : 'POST',
            mode: 'cors', // no-cors, cors, *same-origin
            cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
            credentials: 'same-origin', // include, *same-origin, omit
            headers: {
              'Content-Type': 'application/json',
            },
            body : JSON.stringify({
              messageID : msg.messageID
              })
            })   
    }
    getProfileImages()
  })

  // Add profile pictures 

function getProfileImages(){

    if (sessionStorage.getItem('profilePicture')) {
        // Get the profile picture url if it is there.
        profilePicture = sessionStorage.getItem('profilePicture');
      
        const images = document.querySelectorAll(".chat-current-user-pic")
      

        for (let image of images){
            image.style.backgroundImage = `url(${profilePicture})`
        }   
      
    } else {
        fetch('/get-profile-pic-thumb.json')
        .then(function(response) {
          return response.json();
        })
        .then(function(myJson) {
      
          const images = document.querySelectorAll(".chat-current-user-pic")
      
          for (let image of images){
              image.style.backgroundImage = `url(${JSON.stringify(myJson)})`
          }

          sessionStorage.setItem('profilePicture', JSON.stringify(myJson))
        });
    }

    if (sessionStorage.getItem('otherUserProfilePicture')) {
        // Get the profile picture url if it is there.
        otherProfilePicture = sessionStorage.getItem('otherUserProfilePicture');
      
        const images = document.querySelectorAll(".chat-other-user-pic")

        for (let image of images){
            image.style.backgroundImage = `url(${otherProfilePicture})`
        }
    } else {
        fetch(`/get-profile-pic-thumb-other/${otherUser}`)
        .then(function(response) {
          return response.json();
        })
        .then(function(myJson) {
           
      
          const images = document.querySelectorAll(".chat-other-user-pic")
      
          for (let image of images){
              image.style.backgroundImage = `url(${JSON.stringify(myJson)})`
          }

          sessionStorage.setItem('otherUserProfilePicture', JSON.stringify(myJson))
        });
    }
  }

  getProfileImages()




