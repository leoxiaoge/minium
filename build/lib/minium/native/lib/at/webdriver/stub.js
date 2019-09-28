var jsstub = ( function(that){

	if(window.jsstub != undefined){
		return window.jsstub
	}


	function wrap_ret(ret){
		return JSON.stringify(ret)
	}

	function isNullOrUndefined(a){
		if(null === a){
			return true;
		}else if (undefined === a){
			return true
		}
		return false;
	}

	var errorCode = {
		success: 0,
		unknown: -1,
		failed: 1,
		error: 2,
		notExists: 3
	};

	var g_config = {
		autoScroll: true
	};

	var returnResponse = function (ret, msg, data) {
		if(isNullOrUndefined(ret)){
			ret = errorCode.success
		}
		if(isNullOrUndefined(msg)){
			msg = "success"
		}
		if(isNullOrUndefined(data)){
			data = ""
		}

		this.ret = ret;
		this.msg = msg;

		this.data = data;
		var that = this;

		this.serialize = function () {
			var d = this.data;
			if(undefined == this.data){
				d = null;
			}
			return wrap_ret({
					ret: that.ret,
					msg: that.msg,
					data: d
				})
		}
	};

	/*******************************************************************************
	 * 对外的api
	 */
	function textSelector(text) {
		var elems = [];
		var range = document.createRange();
		var walk=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT, null,false);
		while(n=walk.nextNode()){
			try{
				var textContent = n.textContent;
				if(textContent == text){
					elems.push(new _Element(n, range));
				}
			}catch(ignored){
				console.log(ignored);
			}
		}
		return elems;
	}

	function textContainsSelector(text) {
		var elems = [];
		var range = document.createRange();
		var walk=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT, null,false);
		while(n=walk.nextNode()){
			try{
				var textContent = n.textContent;
				if(textContent.indexOf(text) !== -1){
					elems.push(new _Element(n, range));
				}
			}catch(ignored){
				console.log(ignored);
			}
		}
		return elems;
	}

	that.api = {

		dumpDomJson: function (selectorString) {
			var elems = document.querySelectorAll(selectorString);
			var elemWrapList = [];
			var elemDicts = [];
			for(var i=0; i<elems.length; i+=1){
				elemWrapList.push(new _Element(elems[i]))
			}

			// just got max index elment
            var zIndexGroup = {};
			for(var i=0; i<elemWrapList.length; i+=1){
				var zIndex = elemWrapList[i].max_index;
				if(!zIndexGroup[zIndex]){
					zIndexGroup[zIndex] = [];
				}
				zIndexGroup[zIndex].push(elemWrapList[i]);
            }

            for(var i=0; i<elemWrapList.length; i+=1){
				var el = elemWrapList[i];
				var zIndex = el.max_index;
				var hasCovered = false;
				for(var otherZindex in zIndexGroup){
					if(otherZindex>zIndex){

						for(var j=0; j<zIndexGroup[otherZindex].length; j+=1){
							var otherEl = zIndexGroup[otherZindex][j];
							if(otherEl.visible){
								var otherElRect = otherEl.max_index_rect;
								var x = el.rect.left + el.rect.width / 2;
								var y = el.rect.top + el.rect.height / 2;
								if(x>otherElRect.left && x < otherElRect.left+otherElRect.width){
									if(y>otherElRect.top && y<otherElRect.top+otherElRect.height){
										console.log(el, "covered by", otherEl);
										hasCovered = true;
										break;
									}
								}
							}

						}

					}
				}
				if(!hasCovered){
					elemDicts.push(el.toDict());
				}
            }

			return elemDicts;
		},

		elementOperation: function (selectorString, action, actionArgs, instance) {
			var elems = null;
			var hasMatch = false;
			console.log(selectorString, action, actionArgs, instance);

			// 基本的selector不能满足需求，需要增加额外的
			var supplySelectors = [
				[/:text\(\s*['"](.*)['"]\s*\)/, textSelector],
				[/:contains\(\s*['"](.*)['"]\s*\)/, textContainsSelector]
			];
			for(var i=0; i<supplySelectors.length; i+=1){
				var supplySelector = supplySelectors[i];
				var r = selectorString.match(supplySelector[0]);
				if(r){
					// 命中附加的selector
					var text = r[1];
					console.log("hit supply selector", text);
					elems = supplySelector[1](text);
					hasMatch = true
				}
			}
			if(!hasMatch){
				elems = document.querySelectorAll(selectorString);
			}

			console.log(elems);
			var res = new returnResponse();
			if(elems.length>0){
				var elem;
				if(isNullOrUndefined(instance)){
					elem = elems[0];
				}else{
					elem = elems[instance];
				}

				var wrapElement = null;
				if(elem.constructor.name == '_Element'){
					wrapElement = elem;
				}else{
					wrapElement = new _Element(elem);
				}

				if(isNullOrUndefined(action)){
					// 如果不传action，就返回元素本身
					res.data = wrapElement.toDict();
				}else{
					if(action == "_setProperty"){
						res.data = wrapElement.elem[actionArgs[0]] = actionArgs[1];
					}else if (action == "_getProperty"){
						res.data = wrapElement.elem[actionArgs[0]];
					}
					else{
						//res.data = wrapElement.elem[action](...actionArgs);
						res.data = wrapElement.elem[action].apply(wrapElement.elem, actionArgs);
					}
				}
			}else{
				res.ret = errorCode.notExists;
				res.msg = selectorString + " not exists"
			}
			console.debug(res);
			return res
		},

		setConfig: function (name, value) {
			g_config[name] = value
		},

		scrollDown: function () {
			var wsize = getWindowSize();
			if(isNullOrUndefined(wsize)){
				return new returnResponse(errorCode.failed, "无法获取屏幕大小");
			}
			var rect = document.body.getBoundingClientRect()
			var y = wsize.height - rect.top
			var x = wsize.width / 2
			console.log('scroll', x, y)
			window.scroll(x, y)
		},
		scrollTo:function (x, y) {
			window.scroll(x, y)
		}
	};


	/**
	 * 总入口
	 */

	that.apiCalled = function(func_name){
		try{
			var args = [];
			for(var i=1; i<arguments.length; i+=1){
				args.push(arguments[i]);
			}
			var data = jsstub.api[func_name].apply(jsstub.api, args);
			//var data = jsstub.api[func_name](...params);
			console.log(data.constructor)
			if(!isNullOrUndefined(data)){
				if(data.constructor == returnResponse){
					return data.serialize()
				}
			}
			return new returnResponse(errorCode.success, "success", data).serialize();
		}catch (err){
			return new returnResponse(errorCode.error, err.message, new Error().stack).serialize();
		}
	}


	/**
	 * ***************************
	 * 元素操作接口
	 *
	 */

	var __g_window_size = null;

	function getWindowSize(){
		if(null == __g_window_size){
			__g_window_size = {
				width: window.innerWidth,
				height: window.innerHeight,
			}
		}
		return __g_window_size
	}

	function _Element(e, range){

		if(isNullOrUndefined(e)){
			return "null";
		}
		var rect;
		var element;
		if(!isNullOrUndefined(range)){
			range.selectNodeContents(e);
			rect = range.getBoundingClientRect();
			element = e.parentNode
		}else{
			element = e;
			rect = e.getBoundingClientRect()
		}
		var htmlAttributes = element.attributes;
		var attributes = {};
		for (var i = 0, htmlAttribute; htmlAttribute = htmlAttributes[i]; i++){
			var attrName = htmlAttribute.name;
			if(!(attrName in attributes)){
				attributes[attrName] = []
			}
			attributes[attrName].push(htmlAttribute.value)
		}
		this.text = element.innerText;
		this.textContent = element.textContent;
		this.elem = element;
		this.rect = rect;
		this.attributes = attributes;
		this.x = rect.left + rect.width/2;
		this.y = rect.top + rect.height/2;
		this.id = element.id;
		this.tagName = element.tagName;
		this.style = getComputedStyle(this.elem);
		this.max_index = 0;
		this.max_index_rect = rect;
		var el = element;
        do {
            var style = getComputedStyle(el);
			if(style && style.position && style.zIndex){
			    var z_index = parseInt(style.zIndex);
			    if(z_index > this.max_index){
			        console.log("z-index:"+z_index);
			        this.max_index = z_index;
			        this.max_index_rect = el.getBoundingClientRect();
                }
		   }
		} while (el = el.parentElement);

        const t = this.isShow();
        console.log(this.attributes.t_cid, t)
		this.visible = t;
	}
	_Element.prototype.toDict = function(){
		var point_in_screen = function (x, y) {
			if(0<=x && x<=window.innerWidth && 0<y && y<window.innerHeight){
				return true;
			}
			return false;
        };

		var size = getWindowSize();
		//var part_in_screen = this.rect.top >= window.innerHeight || this.rect.left >=0 || this.rect.top<= size.height && this.rect.left <= size.width
		var part_in_screen = point_in_screen(this.rect.left, this.rect.top) || point_in_screen(this.rect.right, this.rect.bottom)
		var all_in_screen = part_in_screen && this.rect.bottom <= size.height && this.rect.right <=size.width;
		// rect 是相对viewport的位置
		const rt = {
			height: this.rect.height,
			width: this.rect.width,
			left: this.rect.left,
			top: this.rect.top,
			bottom: this.rect.bottom,
			right: this.rect.left + this.rect.width
		};
		if(rt.top<0){
			rt.height = rt.height + rt.top;
			rt.top = 0;
		}
		if(rt.bottom>size.height){
			rt.height = rt.height - (rt.bottom-size.height);
			rt.bottom = size.height;
		}
		if(rt.left<0){
			rt.left = 0;
			rt.width = rt.width + rt.left;
		}
		if(rt.right>size.width){
			rt.right = size.width;
			rt.width = rt.width - (rt.right - size.width);
		}

		return {
			rect: rt,
			attributes: this.attributes,
			x: this.x,
			y: this.y,
			id: this.id,
			screen_height: size.height,
			screen_width: size.width,
			document_height: size.height,
			pageXOffset: window.pageXOffset,
			pageYOffset: window.pageYOffset,
			document_width: size.width,
			tagName: this.tagName,
			text: this.text,
			part_in_screen: part_in_screen,
			up_screen: this.rect.bottom < 0,
			down_screen: this.rect.top > window.innerHeight,
			in_screen: all_in_screen,
			visible:  this.visible
		};
	};

	_Element.prototype.scrollVisible = function(){
		this.elem.scrollIntoView(true);
		this.rect = this.elem.getBoundingClientRect()
	};

	_Element.prototype.isShow = function(){
		const x = this.rect.left+this.rect.width/3;
		const y = this.rect.left+this.rect.height/3;

		if(x<=0){
			return false
		}

		if(this.rect.width<=0 || this.rect.height<=0){
			console.log("not show width:"+this.rect.width + ", height:"+this.rect.height);
			return false
		}

		console.log(x, y);

		if(this.elem === document.elementFromPoint(x, y)){
			//这个是会误判的，放到1/3的地方，降低重合概率
			console.log("isShow hit elementFromPoint")
			return true
		}

        if(this.style){
            if(this.style.opacity === 'none' || this.style.visibility === 'hidden' || this.style.display === 'none'){
			    console.log("not show hit style", this.style);
			    return false
		    }
        }



		var e = this.elem;
		do {
			if(!e.offsetParent && e.offsetWidth === 0 && e.offsetHeight === 0){
				console.log("isShow hit offset, offsetWidth:" + e.offsetWidth+ ", offsetHeight:" + e.offsetHeight+"length:"+e.getClientRects().length);
				return false
		   }
		} while (e = e.parentElement);

		return true;
	};

	_Element.prototype.isBody = function() {
		var e = this.elem;
		return e.tagName == 'BODY'
	};

	console.log("stub init")

	return that
})(window.jsstub || {});


/**
 * ***************************
 * 性能测试接口，目前只有wenwen有可能用
 *
 */


function getPerformanceTiming() {
    var performance = window.performance;

    if (!performance) {
        // 当前浏览器不支持
        console.log('你的浏览器不支持 performance 接口');
        return;
    }

    var t = performance.timing;
    var times = {};

    //【重要】页面加载完成的时间
    //【原因】这几乎代表了用户等待页面可用的时间
    times.loadPage = t.loadEventEnd - t.navigationStart;

    //【重要】解析 DOM 树结构的时间
    //【原因】反省下你的 DOM 树嵌套是不是太多了！
    times.domReady = t.domComplete - t.responseEnd;

    //【重要】重定向的时间
    //【原因】拒绝重定向！比如，http://example.com/ 就不该写成 http://example.com
    times.redirect = t.redirectEnd - t.redirectStart;

    //【重要】DNS 查询时间
    //【原因】DNS 预加载做了么？页面内是不是使用了太多不同的域名导致域名查询的时间太长？
    // 可使用 HTML5 Prefetch 预查询 DNS ，见：[HTML5 prefetch](http://segmentfault.com/a/1190000000633364)
    times.lookupDomain = t.domainLookupEnd - t.domainLookupStart;

    //【重要】读取页面第一个字节的时间
    //【原因】这可以理解为用户拿到你的资源占用的时间，加异地机房了么，加CDN 处理了么？加带宽了么？加 CPU 运算速度了么？
    // TTFB 即 Time To First Byte 的意思
    // 维基百科：https://en.wikipedia.org/wiki/Time_To_First_Byte
    times.ttfb = t.responseStart - t.navigationStart;

    //【重要】内容加载完成的时间
    //【原因】页面内容经过 gzip 压缩了么，静态资源 css/js 等压缩了么？
    times.request = t.responseEnd - t.requestStart;

    //【重要】执行 onload 回调函数的时间
    //【原因】是否太多不必要的操作都放到 onload 回调函数里执行了，考虑过延迟加载、按需加载的策略么？
    times.loadEvent = t.loadEventEnd - t.loadEventStart;

    // DNS 缓存时间
    times.appcache = t.domainLookupStart - t.fetchStart;

    // 卸载页面的时间
    times.unloadEvent = t.unloadEventEnd - t.unloadEventStart;

    // TCP 建立连接完成握手的时间
    times.connect = t.connectEnd - t.connectStart;

    // 白屏时间
    times.whitepage = t.domLoading - t.fetchStart;


    var ret = {
        loadPage: times.loadPage,
        whitepage: times.whitepage,
        domReady: times.domReady,
        request: times.request,
        redirect: times.redirect,
        lookupDomain: times.lookupDomain,
        ttfb: times.ttfb,
        loadEvent: times.loadEvent,
        appcache: times.appcache,
        unloadEvent: times.unloadEvent,
        connect: times.connect
    }

    return wrap_ret(ret)
}
