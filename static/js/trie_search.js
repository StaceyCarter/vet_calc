const search = document.querySelector('#search')
const results = document.querySelector('#results')

class Node {
  constructor(value = ''){
    this.value = value;
    this.children = [];
    this.end = false;
  }
  setEnd() {
      this.end = true;
  }
  isEnd() {
      return this.end;
  }
}

class Trie {
  constructor() {
    this.root = new Node();
  }

   add(value, parent = this.root) {
    for (let i = 0; i < value.length; i++){
      // looks into all of the parents children and finds one that matches the current letter of the input word.
      let node = parent.children.find(child => child.value[i] === value[i])
      // if the node wasn't found, create one.
      if (!node) {
        node = new Node(value.slice(0, i+1));
        parent.children.push(node);
      }
      if (i === (value.length - 1)){
          node.setEnd()
      }
      parent = node
    }
   }
  // this.root = the root of the entire trie
  find(value, parent = this.root) {
      // loop through every letter in the value
    for (let i = 0; i < value.length; i++){
        //
      parent = parent.children.find(child => child.value[i] === value[i]);

      if (!parent){
          return null;
      }
    }
    return parent;
  }

  findWords(value, parent=this.root) {
    let top = this.find(value, parent)
    //if no matches are found, return nothing.
    if (!top) return [];

    function getWords(node) {
        let words = [];
        if (node.isEnd()){
            words.push(node);
        }
        for (let child of node.children){
            words = [...words, ...getWords(child)]
        }
        return words;
    }
    return getWords(top)
  }
}



const trie = new Trie();

search.addEventListener('keyup', () => {
    results.innerHTML = '';

    // Returns an array of words.
    const nodes = trie.findWords(search.value);

    if (!nodes.length) return;

    for (let node of nodes) {
        // results.innerHTML += `<li>${node.value}</li>`
        console.log(node.value)
    }
})


fetch('/get-drug-names')
    .then((res) => {
        return res.json();
    })
    .then((str) => {
        return JSON.parse(str)
    })
    .then((data) => { 
        console.log(data) 
        console.log(typeof data)    
        for(let drug of data){
            trie.add(drug)
        }
    })