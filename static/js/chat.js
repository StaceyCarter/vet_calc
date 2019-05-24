let socket = io.connect('http://' + document.domain + ':' + location.port);

const url = window.location.href.split('/')
const chatID = url.pop()

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
      $('div.message_holder').append( '<p><b style="color: #000">' + msg.username + '</b>: ' + msg.message + '</p>')
    }
  })