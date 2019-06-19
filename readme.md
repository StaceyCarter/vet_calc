# VetCalc

<p align="center">
  <img src="/static/logos/pinkStethGreyText.jpg"/>
</p>

VetCalc is a social network for the veterinary industry where users can save, share and calculate drug doses. The calculator provides a visualisation of the amount of tablets or liquid required per dose, allowing for more informed decisions when selecting drug concentration. A label is automatically generated and can be texted directly to the client, reducing communication errors.
Users can save other vets' preferred doses to their own page for future reference. While nurses can prescribe according to a vet’s preferences, they cannot save their own doses. Interaction between users is enabled through private messaging and following.
VetCalc saves vets approximately 5 hours a week and reduces medical mistakes.

## Motivation

As a practicing veterinarian, I was frustrated with the amount of time I spent looking up drug doses. Once I would find a dose I liked, if I didn't use it for a while, I would need to look it up all over again. 
Deciding on a drug dose isn't as simple as just consulting a textbook. Usually the textbook ranges are quite large and it can be difficult to decide where to go within the range. Deciding on a dose often involves consulting multiple texbooks (since they can all have different ranges) and consulting with colleagues or specialists from other hospitals on what their preferred dose is.
Both vets and nurses are responsible for calculating the actual amount of drug required for a given dose, which can lead to another subset of complications regarding miscalculations. For example, overdosing or underdosing or not sending the correct total amount of drug home with the patient. Mistakes made here can have severe consequences.  

## Tech/framework used

<ul>

  <li>Python </li>
  <li> Flask
    
  </li>
  <li> Javascript
  
  </li>
  <li> React
  
  </li>
  <li> Socketio
  
  </li>
  <li> HTML
  
  </li>
  <li> CSS
  
  </li>


 </ul>

## How to use

## Features

### Complex database model
There is a lot that goes into deciding on a drug dose and I really wanted my database to support this.
I spent a long time thinking about and working through an ideal datamodel. In the time I had for the scoped version of this project, there wasn't enough time to implement every table and feature I wanted, but I plan to continue working towards the more complex version after Hackbright.

The ideal datamodel:
<p align="center">
  <img src="/static/future_user_database.png"/>
</p>

<p align="center">
  <img src="/static/future_drug_database.png"/>
</p>


The current implementation of the datamodel:
<p align="center">
  <img src="/static/datamodel_current.png"/>
</p>

### Autocomplete searching using a trie
Since drug names can be difficult to spell, I wanted to implement an autocomplete search. I researched and implemented a data structure called a trie. Which is a tree data stucture that allows for quick searching. 

[![Image from Gyazo](https://i.gyazo.com/85243a7670ed5ffe9f4442c0af98c542.gif)](https://gyazo.com/85243a7670ed5ffe9f4442c0af98c542)

### Private messaging with Socketio
Private messaging is implemented with socketio and javascript in the frontend and flask-socketio in the backend. 

[![Image from Gyazo](https://i.gyazo.com/8ae0080b9db817bb262f00d4cdc5c2e7.gif)](https://gyazo.com/8ae0080b9db817bb262f00d4cdc5c2e7)

### Infinite scroll
I implemented the infinite scroll by adding an event listener that detects when the user scrolls to the top of the page. When this happens an AJAX request is sent to the server which uses a paginated database query to get the next 10 messages. When no messages are left to be returned, a "No more messages" notification appears at the top.  
[![Image from Gyazo](https://i.gyazo.com/0b975a41b142467162c36870c1711432.gif)](https://gyazo.com/0b975a41b142467162c36870c1711432)

### Message notifications
When a user 

[![Image from Gyazo](https://i.gyazo.com/f6ce276e68a19a92be0b768c77cc364e.gif)](https://gyazo.com/f6ce276e68a19a92be0b768c77cc364e)


### User uploaded images with Pillow and Amazon S3 bucket

### Visual calculator with React, Anime.js, Lodash and CSS clip paths

[![Image from Gyazo](https://i.gyazo.com/7990078b6b34ad95f248b6cbe1c8e2b9.gif)](https://gyazo.com/7990078b6b34ad95f248b6cbe1c8e2b9)

Visualise the number of tablets required per dose. You can choose whether the tablets can be halved or quartered, or can only be taken whole.

[![Image from Gyazo](https://i.gyazo.com/9556d7e681c5e7495493e096332a5241.gif)](https://gyazo.com/9556d7e681c5e7495493e096332a5241)

### Editable instruction label
As you use the calculator page, the label instructions at the bottom update according to the state of the rest of the page. You can customize the label further before texting it to the client if there is extra information you want to include.

[![Image from Gyazo](https://i.gyazo.com/4aea8292d8057de35798ea89f449709f.gif)](https://gyazo.com/4aea8292d8057de35798ea89f449709f)


### Text label instructions to client
Labels are subject to degradation. They fade, become smudged and owners throw out the packaging. When label instructions are unclear or non-existent, an owner's reliance on memory drastically increases the risk of medical mistakes.  

[![Image from Gyazo](/static/text_client.gif)]


### Following

[![Image from Gyazo](https://i.gyazo.com/d296e5b816f7f1da41a68b5e71ea8ca7.gif)](https://gyazo.com/d296e5b816f7f1da41a68b5e71ea8ca7)


### Save preferred drug doses

[![Preferred drug gif](/static/save_dose.gif)]

### Save other vet's preferred drug doses

[![Image from Gyazo](https://i.gyazo.com/53b01d98daf4a21202b6795a4c9aeedd.gif)](https://gyazo.com/53b01d98daf4a21202b6795a4c9aeedd)

### User permissions
Vets and nurses have distinct accounts. Veterinarians can utilize all features of the app. While nurses arae unable to set their own preferred doses, they can save preferred doses from the vets they work with. In the future I plan to build out this feature into special, vet-nurse connections where nurses can set who they are working with on a shift, and automatically get shown that vet's preferred doses. 

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

```python



```

## Credits



Blog posts and tutorials: 
* Socket related:
https://secdevops.ai/weekend-project-part-2-turning-flask-into-a-real-time-websocket-server-using-flask-socketio-ab6b45f1d896

Image credits:
* Syringe image on calculator page - Icon made by Freepik from www.flaticon.com
* Stethoscope logo - https://cutthatdesign.com/2018/04/nurse-stethoscope-heartbeat-design-set/
* Landing page photos - All photos from unsplash.com



## License
[MIT](https://choosealicense.com/licenses/mit/) Stacey Carter 2019