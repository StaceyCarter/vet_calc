let socket = io.connect('http://' + document.domain + ':' + location.port);

const url = window.location.href.split('/')
const chatID = url.pop()

const scrollTop = $(document).scrollTop();

window.scrollTo(scrollTop, document.body.scrollHeight)

let page = 1;

console.log(" scrolltop: ", scrollTop)
document.addEventListener("scroll", () => window.scrollY === 0 ? loadMessages() : "")

function loadMessages(){
    console.log("calling load messages")
    // Sent request to server to retrieve the next 10 messages
    // prepend the next 10 messges to the message_holder.
    $.get(`/chat/messages/${chatID}/${page}.json`, (data) => {
        console.log(data)

        // loops through the number keys in the json object and prepends them to the page.
        for (let item of Object.keys(data)){
            if (!isNaN(parseInt(item))){
                console.log(item)
                console.log(data[item])

                $('div.message_holder').prepend( `<div class="sent-message ${ data['currentUser'] == data[item][0] ? 'current-user-sender col-md-5' : 'other-user-sender col-md-offset-5 col-md-7 '}"><b style="color: #000">` + data[item][1] + '</b>: ' + data[item][2] + '</div>')

            }
        }
    })
}

socket.on('connect', () => {
    console.log('WEB SOCKET CONNECTED')
    socket.emit('join', { room: chatID })
    })

socket.on('disconnect', () => {
console.log('DISCONNECTED')})


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
    console.log(msg)

    if ( typeof msg.username !== 'undefined'){
      $('h3').remove()
      $('div.message_holder').append( `<div class="sent-message ${ currentUser === msg.sender ? 'current-user-sender col-md-5' : 'other-user-sender col-md-offset-5 col-md-7 '}"><b style="color: #000">` + msg.username + '</b>: ' + msg.message + '</div>')
    }
  })

