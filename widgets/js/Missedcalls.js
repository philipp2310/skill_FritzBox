class FritzBox_Missedcalls extends Widget {
	constructor(uid, widgetId, widget) {
		super(uid, widgetId)
		let self = this
		this.uid = uid
		this.widgetId = widgetId
		this.widget = widget
		this.myDiv = document.querySelector(`[data-ref="FritzBox_Missedcalls_${this.uid}"]`)
		this.myList = this.myDiv.querySelector(`[data-ref="FritzBox_Missedcalls_List_${this.uid}"]`)
		this.aliceSettings = JSON.parse(window.sessionStorage.aliceSettings);
		this.currentlyShowingButtons = false
		this.buildButtons()
		this.callHeight = 42
		this.dispPerPage = Math.floor(this.myList.clientHeight / this.callHeight)
		this.dispFrom = 0
		this.data = null
		this.interval = setInterval(()=>this.refresh(), 5000)
		this.refresh()
	}

	buildButtons() {
		if( this.widget.configs?.showButtons ) {
			let self = this
			this.currentlyShowingButtons = true
			let back = document.createElement('button');
			back.innerText = "Back"
			back.onclick = function () {
				self.prevPage()
			}
			let next = document.createElement('button');
			next.onclick = function () {
				self.nextPage()
			}
			next.innerText = "Next"
			let pageNum = document.createElement('span');
			pageNum.innerHTML = '<span data-ref="pageCurrent_'+this.uid+'">x</span> / <span data-ref="pageTotal_'+this.uid+'">y</span>'
			let actionBar = this.myDiv.querySelector('.actionBar')
			actionBar.appendChild(back)
			actionBar.appendChild(pageNum)
			actionBar.appendChild(next)
		} else {
			this.myDiv.querySelector('.actionBar').innerHTML = ""
			this.currentlyShowingButtons = false
		}
	}

	stop() {
		clearInterval(this.interval)
	}

	onResize(target, width, height, delta, direction){
		this.rerender()
	}

	nextPage() {
		this.dispFrom += this.dispPerPage
		this.refresh()
	}

	prevPage() {
		this.dispFrom -= this.dispPerPage
		this.refresh()
	}

	getDiv(index){
		let self = this
		let seen = this.data[index].new ? "new" : "seen"
		let date = this.data[index].date.substr(0,6)
		let time = this.data[index].date.substr(9,5)
		let div = document.createElement('div');
		div.id = 'call_' + index
		div.classList.add('call')
		div.classList.add(seen)
		div.onclick = () => this.callClicked(this.data[index].id)
		div.innerHTML = "<div class='mcDate'>" + date + "</div>" +
						"<div class='mcTime'>" + time + "</div>" +
						"<div class='mcCaller'>" + this.data[index].name + "</div>"
		return div
	}

	callClicked(index){
		this.mySkill.markRead( { "index": index })
		this.refresh()
	}

	rerender() {
		if (this.data == null)
			return
		let content = document.createElement('div');
		let firstCall = this.getDiv(this.dispFrom)
		content.appendChild(firstCall)
		this.myList.innerHTML = ""
		this.myList.appendChild(content)
		this.callHeight = firstCall.getBoundingClientRect().height
		let margin = parseFloat(getComputedStyle(firstCall).marginTop)
		this.dispPerPage = Math.floor(this.myList.offsetHeight / ( this.callHeight + margin))
		let count = 1
		while(count < this.dispPerPage) {
			content.appendChild(this.getDiv(count+this.dispFrom))
			count++;
		}
		//this.myList.innerHTML = ""
		this.myList.appendChild(content)

		let pageCurrent = Math.ceil(this.dispFrom/this.dispPerPage)+1
		let pageTotal = Math.ceil(this.data.length/this.dispPerPage)+1

		if( this.widget['configs']['showButtons'] ) {
			this.myDiv.querySelector(`[data-ref="pageCurrent_${this.uid}"]`).innerHTML = pageCurrent
			this.myDiv.querySelector(`[data-ref="pageTotal_${this.uid}"]`).innerHTML = pageTotal
		}
	}

	refresh() {
		const self = this
		if( this.widget.configs?.showButtons != this.currentlyShowingButtons){
			this.buildButtons()
		}
		this.mySkill.getMissedCalls().then(response => response.json()).then(data => {
			self.data = data.data
			self.rerender()
		})
	}
}
