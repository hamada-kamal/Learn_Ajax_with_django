var updateBtns = document.getElementsByClassName('update-cart')
console.log( "88888888888888"+ updateBtns)
for(i=0;i<updateBtns.length;i++){
    updateBtns[i].addEventListener('click', function(){
        var productId= this.dataset.product
        var action= this.dataset.action
        console.log('productId: ',productId,'action:',action )
        console.log('USER',user)
        if(user == 'AnonymousUser'){
            addCookieItem(productId , action)
			// console.log('loged in please')
        }else{
            updateUserOrder(productId , action)
			console.log('u are loging..')
        }

    })
}

function addCookieItem(productId, action){
	if(action=='add'){
		if(cart[productId]==undefined){
			cart[productId] = {'quantity':1}
		}else{
			cart[productId]['quantity'] +=1
		}

	}

	if(action=='remove'){
		if(cart[productId]['quantity'] >1){
			cart[productId]['quantity'] -=1
		}
		
	}
	if(action=='delete'){
		delete cart[productId]	
		
	}

	console.log('Cart:', cart)
	document.cookie ='cart=' + JSON.stringify(cart) + ";domain=;path=/"
	// location.reload()


}


function updateUserOrder(productId, action){
	console.log('User is authenticated, sending data...')

		var url = '/products/update_item/'

		fetch(url, {
			method:'POST',
			headers:{
				'Content-Type':'application/json',
				'X-CSRFToken':csrftoken,
			}, 
			body:JSON.stringify({'productId':productId, 'action':action})
		})
		.then((response) =>{
		   return response.json();
		})
		.then((data) =>{
		    console.log('datasss:',data)
		})
		// location.reload()
}
