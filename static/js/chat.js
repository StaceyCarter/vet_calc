let socket = io.connect('http://' + document.domain + ':' + location.port);
//
socket.on('connect', () => {
    console.log('WEB SOCKET CONNECTED')
    socket.emit('join', { room: 'test'})
    })

socket.on('disconnect', () => {
console.log('DISCONNECTED')})



//socket.join('room')
//io.to('room').emit('my_event', {
//  data: 'user connected',
//  room: 'room'})

//        let form = $('form').on('submit', (e) => {
//          e.preventDefault()
//          let user_name = $('input.username').val()
//          let user_input = $('input.message').val()
//          socket.emit('my_event', {
//            user_name : user_name,
//            message : user_input
//          })
//          $('input.message').val('').focus()
//        })
//      })

  socket.on('my_response', (msg) => {
    console.log(msg)
    if ( typeof msg.user_name !== 'undefined'){
      $('h3').remove()
      $('div.message_holder').append( '<div><b style="color: #000">' + msg.user_name + '</b> ' + msg.message + '</div>')
    }
  })