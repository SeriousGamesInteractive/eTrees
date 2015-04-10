
var SQUARERADIUS = 15;
var INITIALPOSITION = 30;
var RADIUSCONECTNODE = 6;
var TRANSLATEVALUE = 10;
var CONNECTIONMARGINX = 5;
var scale = 1;
var imageSrc = "";
var stage = null;
var layer = null;
var tooltipLayer = null;
var tooltip = null;
var csrftoken;
var treeConnection = null;
var COLORNODE = {
    0 : "#46b8da",
    1 : "#5cb85c",
    2 : "#eea236"
  };
var positionOptions = {
    "a" : {"x":190,"y":30},
    "b" : {"x":190,"y":80},
    "c" : {"x":190,"y":130},
    "n" : {"x":190,"y":80}
};
var positionTextOptions = {
    "a" : {"x":185,"y":0},
    "b" : {"x":185,"y":50},
    "c" : {"x":185,"y":100},
    "n" : {"x":185,"y":50}
};
var nodeObjects = [];

//
var initialPosX  = 50;
var initialPosY = 50;
var initialPositionCounter = 0;

/**********************
* NodeObj javascript object 
* to save the properties of each
* node locally
***********************/
function NodeObj(id, name, options, type, imgFile) {
    this.id = id;
    this.options = options;
    this.type =type;
    this.name =name;
    this.imgFile = imgFile; 
    this.attributes = [];   

    this.addAttribute = function(attribute) {
        this.attributes.push(attribute);
    };
}

function getNodeId(id) {
    for (var i = 0; i < nodeObjects.length;i++){
        var nodeObjTemp = nodeObjects[i];
        if(id == nodeObjTemp.id) {
            return nodeObjTemp;
        }
    }
    return null;
}

$(document).ready(function(){
    csrftoken= getCookie('csrftoken');
    imageSrc = window.location.origin + "/media/stories/" +$("#project_id").val() + "/";

    treeConnection = new Array();
    var json = '{"attrs":{"width":1000,"height":700},"className":"Stage","children":[{"attrs":{},"className":"Layer","children":[{"attrs":{"strokeWidth":2,"stroke":"green","points":[{"x":448.5,"y":110},{"x":86,"y":150}],"name":"lines","id":"line-c1_node1-node2"},"className":"Line"},{"attrs":{"strokeWidth":2,"stroke":"green","points":[{"x":463.5,"y":110},{"x":520,"y":178}],"name":"lines","id":"line-c2_node1-node3"},"className":"Line"},{"attrs":{"x":451,"y":84,"draggable":true,"id":"group_node1","width":50,"height":50,"offsetX":25,"offsetY":25,"name":"group_node","scaleX":2.357947691000002,"scaleY":2.357947691000002,"rotation":0,"skewX":0,"skewY":0},"className":"Group","children":[{"attrs":{"x":30,"y":30,"sides":4,"radius":15,"fill":"red","stroke":"black","strokeWidth":2,"name":"node","id":"node1"},"className":"RegularPolygon"},{"attrs":{"x":22.5,"y":51,"radius":5,"fill":"orange","stroke":"black","strokeWidth":1,"id":"c1_node1","name":"connection"},"className":"Circle"},{"attrs":{"x":37.5,"y":51,"radius":5,"fill":"blue","stroke":"black","strokeWidth":1,"id":"c2_node1","name":"connection"},"className":"Circle"}]},{"attrs":{"x":214,"y":192,"draggable":true,"id":"group_node2","width":50,"height":50,"offsetX":25,"offsetY":25,"name":"group_node","scaleX":2.357947691000002,"scaleY":2.357947691000002,"rotation":0,"skewX":0,"skewY":0},"className":"Group","children":[{"attrs":{"x":30,"y":30,"sides":4,"radius":15,"fill":"red","stroke":"black","strokeWidth":2,"name":"node","id":"node2"},"className":"RegularPolygon"},{"attrs":{"x":22.5,"y":51,"radius":5,"fill":"blue","stroke":"black","strokeWidth":1,"id":"c1_node2","name":"connection"},"className":"Circle"},{"attrs":{"x":37.5,"y":51,"radius":5,"fill":"blue","stroke":"black","strokeWidth":1,"id":"c2_node2","name":"connection"},"className":"Circle"}]},{"attrs":{"x":708,"y":240,"draggable":true,"id":"group_node3","width":50,"height":50,"offsetX":25,"offsetY":25,"name":"group_node","scaleX":2.357947691000002,"scaleY":2.357947691000002,"rotation":0,"skewX":0,"skewY":0},"className":"Group","children":[{"attrs":{"x":30,"y":30,"sides":4,"radius":15,"fill":"red","stroke":"black","strokeWidth":2,"name":"node","id":"node3"},"className":"RegularPolygon"},{"attrs":{"x":22.5,"y":51,"radius":5,"fill":"blue","stroke":"black","strokeWidth":1,"id":"c1_node3","name":"connection"},"className":"Circle"},{"attrs":{"x":37.5,"y":51,"radius":5,"fill":"blue","stroke":"black","strokeWidth":1,"id":"c2_node3","name":"connection"},"className":"Circle"}]}]},{"attrs":{},"className":"Layer","children":[{"attrs":{"opacity":0.75,"visible":false,"listening":false,"x":699,"y":232},"className":"Label","children":[{"attrs":{"fill":"black","pointerDirection":"down","pointerWidth":10,"pointerHeight":10,"lineJoin":"round","shadowColor":"black","shadowBlur":10,"shadowOffsetX":10,"shadowOffsetY":10,"shadowOpacity":0.2,"x":-49.5,"y":-38,"width":99,"height":28},"className":"Tag"},{"attrs":{"text":"node: node3","fontFamily":"Calibri","fontSize":18,"padding":5,"fill":"white","width":"auto","height":"auto","x":-49.5,"y":-38},"className":"Text"}]}]}]}'
    stage = new Kinetic.Stage({
		container: 'canvas',
		width: 1000,
		height: 700
	});
    origin = new Object();
    origin.x = 0;
    origin.y= 0;
    //Layer to draw the labels for the nodes
    layer = new Kinetic.Layer();
    layer.draggable = false;
    // Add node when the button node is pressed
    requestNodeData();
    
    // add the layer to the stage    
    stage.add(layer);
    $('#zoom-in').click(function(){
        ZoomInOutPerform(stage,1);
    });
    $('#zoom-out').click(function(){
        ZoomInOutPerform(stage,-1);
    });
    $('#clear-all').click(function(){
        var layers = stage.getChildren();
        for (var i = 0; i < layers.length;i++){
            var children = layers[i].getChildren();
            while (children.length >0){
                children[0].remove();
            }
        }
        stage.draw();
        $('.element_list_activate').toggleClass("element_list");
        $('.element_list_activate').toggleClass("element_list_activate");
    });
    // Control of buttons
    $('#clear').click(function(){
        var shapes = stage.get('.lines');
        shapes.each(function(shape){
            shape.remove();
            stage.draw();
        });

    });
    /*$('#preview').click(function(){
        requestStageData($('#project_id').val(),printPreview);        
    });*/
    //Print the preview tree conenction save, if exist one.
    requestStageData($('#project_id').val(),printPreview); 
    //Control the submit of the tree checking if everything is correct
    $('#submit-tree').submit(function(){
        /* TODO remove the check of all node connected
        if(!isAllConnected(stage)){
            $.prompt("You need to make all the connections to save the tree.");
            return false;
        }
        */

        /* TODO retired the option of checking end node and initial node are included
        if(!insertedEndInitNode(stage)){
            $.prompt("The ending and initial node has to be inserted and connected.")
            return false;
        }
        */
        var answer =confirm("Do you want to save the tree?");
        if(!answer){
            return false;
        }
       
       var json = stage.toJSON();
       sendStageData(json,$('#project_id').val());
    });
    
    //Add the control of the zoom with the wheel of the mouse
    ZoomInOutWheelEvent(stage);
    MoveCanvas(stage);
});

/*
    Instantiate the line that connect the two nodes selected.
*/
function CreateConnection(node1,node2){
    if (node1 == undefined || node1.length == 0) {
        console.log("node1 undefined");
        return;
    }
    if (node2 == undefined || node2.length == 0) {
        console.log("node1 undefined");
        return;
    }
    if(node1.getId().split("_")[1] == node2.getId()){
        return null;
    }
    if(node2.getAttr("typeNode")==1){
        $.prompt("It cannot be connected to an initial node.");
        return null;
    }
    var line = new Kinetic.Line({
        
        drawFunc: function(canvas){
            var context = canvas.getContext();
            var point1 = node1.getAbsolutePosition();
            var point2 = node2.getAbsolutePosition();
            context.beginPath();
            context.moveTo(point1.x, point1.y);
            context.lineTo(point2.x + ((node2.getWidth() * scale) / 2),point2.y + ((node2.getHeight() * scale) / 2));
            context.closePath();
            canvas.fillStroke(this);
        },
        
        strokeWidth: 2,
        stroke: 'black',
        points:[
            node1.getAbsolutePosition().x ,
            node1.getAbsolutePosition().y,
            node2.getAbsolutePosition().x + (node2.getWidth()  / 2) ,
            node2.getAbsolutePosition().y + (node2.getHeight() / 2)
        ],
        name: "lines",
        id: "line-"+node1.getId()+"-"+node2.getId()
    });

    //Confirm node is connected
    node1.setAttr("isConnected",true);
    return line;
}

/*
* Generate the node: 
*   Arguments:  Stage (The canvas object)
*               layer ( The instantiation of layer on the canvas)
*               connections (number of connections available for the node)
*               nodeid (Id for the node)
*
*   Create a polygon object and attach it circle objects depending on the number of connections
*   All of them are group inside of a Group object
*/
function GenerateNode(stage,layer,connections,nodeid,nodeObj){
    //Create a group to have the regular polygon and the small circle as one element
    var groupNode = new Kinetic.Group({
        x: initialPosX * initialPositionCounter,
        y: initialPosY * initialPositionCounter,
        draggable:true,
        id: "group_"+nodeid,
        width: 50,
        height: 50,
        offset: [50 / 2, 50 / 2],
        name:"group_node"

    });
     //REcalculate the position of the next node to add to the canvas depends on the position of the ones already added
    groupNode.firstTouch = true;
    var groupContent = [];
    var mainImage = new Image();
    mainImage.onload=function(){
       var monkey = new Kinetic.Image({
            x:INITIALPOSITION,
            y:INITIALPOSITION,
            image: mainImage,
            stroke: COLORNODE[nodeObj.type],
            strokeWidth: 4,
            name:"node",
            width: 150,
            height:100,
            id:nodeid
        });
      
        monkey.setAttr('typeNode',nodeObj.type);
        groupContent.push(monkey);
        var nameText = new Kinetic.Text({
            x: monkey.getWidth() / 4,            
            y: 10,
            text: $('#node'+nodeid).text(),
            fontSize: 18,
            fontFamily: 'Calibri',
            fill: 'black',
            name:"title"
        });

        groupContent.push(nameText);
       
        //nameText.moveToTop();
        //Instantiate the label for the NODE and set up its elements
        
        //Generate the connection when a smal circle is orange.
        //Create connection between the small circle and the big node.
        groupNode.on('dragstart', function(event){
        });
        groupNode.on('dragend', function(event){
            var mainshape = event.targetNode;
            var shapes = stage.get('.connection');
            if(mainshape!== undefined && mainshape.getName() == "node") {
                shapes.each(function(cnt){
                    if (cnt.getFill() == 'orange' && cnt.getId().indexOf(mainshape.getId() == -1) ){
                            var existLines = stage.get(".lines");
                            cnt.setFill('blue');
                            existLines.each(function(line){
                                if (line.getId().indexOf(cnt.getId())!=-1){
                                    line.remove();
                                }
                            });
                            var line = CreateConnection(cnt,mainshape);
                            if (line){
                                layer.add(line);
                                line.moveToBottom();
                                layer.draw();
                            }
                    }
                });
            }
        });
        monkey.on('click',function(evt){
            
                var mainshape = evt.targetNode;
                var shapes = stage.get('.connection');
                shapes.each(function(cnt){
                    if (cnt.getFill() == 'orange' && cnt.getId().indexOf(mainshape.getId() == -1 && mainshape.getName() == "node") ){
                        var existLines = stage.get(".lines");
                        cnt.setFill('blue');
                        existLines.each(function(line){
                            if (line.getId().indexOf(cnt.getId())!=-1){
                                line.remove();
                            }
                        });
                        var line = CreateConnection(cnt,mainshape);
                        if (line){
                            layer.add(line);
                            line.moveToBottom();
                            layer.draw();
                        }
                    }
                });            
        });
        
        monkey.on('mouseover', function() {
            document.body.style.cursor = 'pointer';
            //groupNode.setDraggable(true);
            
        });
        monkey.on('mouseout', function() {
            document.body.style.cursor = 'default';
            //groupNode.setDraggable(true);
        });
       

        for(var i = 0; i < nodeObj.attributes.length && connections > 0; i++) {
            idOption = nodeObj.attributes[i].attributeId;
            var idConnection = idOption + '_' + nodeid;
            var positionCircle = positionOptions[idOption];        
            var cnt = new Kinetic.Circle({
                x: positionCircle.x,
                y: positionCircle.y,
                radius:RADIUSCONECTNODE,
                fill:'blue',
                stroke: 'black',
                strokeWidth: 1, 
                id:idConnection,
                name: 'connection'
            });
            cnt.setAttr("isConnected",false);
            var positionTextCircle = positionTextOptions[idOption]
            var cntText = new Kinetic.Text({
                        x: positionTextCircle.x,
                        y: positionTextCircle.y,
                        text: idOption,
                        fontSize: 18,
                        fontFamily: 'Calibri',
                        fill: 'black',
                        name: 'options'
            });
            groupContent.push(cnt);
            groupContent.push(cntText);
        }

        //WHen there is attributes and the node is initial or normal a connection "next" has to be added
        if(nodeObj.attributes.length == 0 && connections >0) {
            idOption ="n";
            var idConnection = idOption + '_' + nodeid;
            var positionCircle = positionOptions[idOption];        
            var cnt = new Kinetic.Circle({
                x: positionCircle.x,
                y: positionCircle.y,
                radius:RADIUSCONECTNODE,
                fill:'blue',
                stroke: 'black',
                strokeWidth: 1, 
                id:idConnection,
                name: 'connection'
            });
            cnt.setAttr("isConnected",false);
            var positionTextCircle = positionTextOptions[idOption]
            var cntText = new Kinetic.Text({
                        x: positionTextCircle.x,
                        y: positionTextCircle.y,
                        text: idOption,
                        fontSize: 18,
                        fontFamily: 'Calibri',
                        fill: 'black',
                        name: 'next'
            });
            groupContent.push(cnt);
            groupContent.push(cntText);
        }
        
        for ( var i = 0; i < groupContent.length; i++){
            groupNode.add(groupContent[i]);
        }
        /*
        monkey.createImageHitRegion(function() {
          
        });
*/
        layer.draw();
         //Apply the scale of the rest of the nodes
        groupNode.setScale(scale);
        
        ConnectionColorChange(stage,groupNode);

    };
    var nc = new Date();
    nc = nc.getTime();
    mainImage.src = imageSrc + "screenshot"+nodeid+".jpg?nc="+nc;
    //mainpolygon.rotate(160);
   /*
    groupNode.on('click',function(){
        groupNode.moveToTop();
       
    });
*/
    groupNode.on('dblclick', function(evt) {
        $(".modal-body").empty();
        $(".modal-body").html('<img src="'+imageSrc + "screenshot"+nodeid+".jpg?nc="+nc + '">');
        $("#nodeModal").modal("show");
    });

    groupNode.on('touchStart mousedown',function() {
        if(this.firstTouch) { 
                initialPositionCounter--;
                this.firstTouch = false;
        }
        this.moveToTop();
        layer.draw();
    });
    return groupNode;
}

/**
* Add the event click to the connection object(circle) to change the color
*
**/
function ConnectionColorChange(stage,group){
    group = typeof group !== 'undefined' ? group : stage;
    var connections = group.get(".connection");
    connections.each(function(connection){
        connection.on('click',function(evt){
            var shapes = stage.get('.connection');
            var shape = evt.targetNode;
            if(shape.getFill() == 'blue'){
                shapes.each(function(shp){
                    shp.setFill('blue');
                });                        
                shape.setFill('orange');
                stage.draw();
            }else{
                shape.setFill('blue');
                stage.draw();
            }
        });
        connection.on('mouseover', function() {
            group.setDraggable(false);
            document.body.style.cursor = 'pointer';
        });
        connection.on('mouseout', function() {
            document.body.style.cursor = 'default';
            group.setDraggable(true);
        });
    });
}

/**
* Perform zoom in/out on the canvas. 
**/
function ZoomInOutPerform(stage,type){
    var zoomFactor = 1.1;
    var zoom = (zoomFactor - (type < 0 ? 0.2 : 0));
    var newscale = scale * zoom;
    
    var groups = stage.get(".group_node");
    groups.each(function(group){
        var origin = group.getPosition();
        var centerPoint = new Object();
        centerPoint.x = stage.getWidth() / 2;
        centerPoint.y = stage.getHeight() / 2;
        origin.x = centerPoint.x - (centerPoint.x - origin.x) * zoom;
        origin.y = centerPoint.y - (centerPoint.y - origin.y) * zoom;
        group.setPosition(origin.x  , origin.y );
        group.setScale(newscale);    
        stage.draw();
    });
    scale *=zoom;
    stage.setAttr('myscale',scale);
}
/**
* Handle the event mousewheel to implement the zoom in/out 
* of the stage, getting the position of the mouse in the canvas to set up
* the center of scale.
**/
function ZoomInOutWheelEvent(stage){
    var zoomFactor = 1.1;
    $(stage.content).on('mousewheel DOMMouseScroll',function(event){
        event.preventDefault();        
        var evt = event.originalEvent,
            mx = evt.clientX ,
            my = evt.clientY 
            var wheel = evt.detail < 0 || evt.wheelDelta > 0 ? 1 : -1;
            //wheel = evt.wheelDelta / 120;
        ZoomInOutPerform(stage,wheel);
    });
}

/**
*
*
**/
function MoveCanvas(stage){
    window.addEventListener('keydown',function(event){
        
        var key = event.keyCode;
        switch(key){
            case 37: // LEFT
                event.preventDefault();
                var groups = stage.get(".group_node");
                groups.each(function(group){
                    group.setX(group.getX()+TRANSLATEVALUE);
                });
                break;
            case 38: // UP
                event.preventDefault();
                var groups = stage.get(".group_node");
                groups.each(function(group){
                    group.setY(group.getY() + TRANSLATEVALUE);
                });
                break;
            case 39: // RIGHT
                event.preventDefault();
                var groups = stage.get(".group_node");
                groups.each(function(group){
                    group.setX(group.getX()-TRANSLATEVALUE);
                });
                break;
            case 40: // DOWN
                event.preventDefault();
                var groups = stage.get(".group_node");
                groups.each(function(group){
                    group.setY(group.getY() - TRANSLATEVALUE);
                });
                break;
            default:
                //NOTHING

        }   
        stage.draw();
    });
       
}

/*
* Add all the events when it shows a preview tree saved.
*/
function AddEventsToPreview(stage,layer){
    //Add the control of the zoom with the wheel of the mouse
    ZoomInOutWheelEvent(stage);
    MoveCanvas(stage);
    scale = stage.getAttr('myscale');
    if (scale== null) {
        scale=1;
    }
    var lines = stage.get('.lines');
    lines.each(function(line){
        var lineIds = line.getId().split("-");
        line.remove();
        var updateConnection =CreateConnection(stage.get("#"+lineIds[1])[0],stage.get("#"+lineIds[2])[0]);
        if (updateConnection){
            layer.add(updateConnection);
            updateConnection.moveToBottom();
            layer.draw();
        }
    });
               
    var nodes = stage.get(".node");
    nodes.each(function(node){
        var imageObj = new Image();
        imageObj.onload = function(){            
            $("#node"+node.getId()).toggleClass("element_list_activate");
            $("#node"+node.getId()).toggleClass("element_list");
            node.on('click',function(evt){
                var mainshape = evt.targetNode;
                var shapes = stage.get('.connection');
                shapes.each(function(cnt){
                    if(cnt.getFill() == 'orange' && cnt.getId().indexOf(mainshape.getId() == -1) && mainshape.getName() == "node"){
                        var existLines = stage.get(".lines");
                        cnt.setFill('blue');
                        existLines.each(function(line){
                            if(line.getId().indexOf(cnt.getId())!=-1){
                                line.remove();
                            }
                        });
                        var line = CreateConnection(cnt,mainshape);
                        if (line){
                            layer.add(line);
                            line.moveToBottom();
                            stage.draw();
                        }
                    }
                });           
            });
            var groupNode = node.parent;
            groupNode.on('dragend', function(event){
                var mainshape = event.targetNode;
                var shapes = stage.get('.connection');
                if(mainshape!== undefined && mainshape.getName() == "node") {
                    shapes.each(function(cnt){
                        if (cnt.getFill() == 'orange' && cnt.getId().indexOf(mainshape.getId() == -1) ){
                                var existLines = stage.get(".lines");
                                cnt.setFill('blue');
                                existLines.each(function(line){
                                    if (line.getId().indexOf(cnt.getId())!=-1){
                                        line.remove();
                                    }
                                });
                                var line = CreateConnection(cnt,mainshape);
                                if (line){
                                    layer.add(line);
                                    line.moveToBottom();
                                    layer.draw();
                                }
                        }
                    });
                }
            });
            
            node.on('mouseover', function() {
                document.body.style.cursor = 'pointer';
            });
            node.on('mouseout', function() {
                document.body.style.cursor = 'default';
            });
            node.on('dblclick', function(evt) {
                $(".modal-body").empty();
                $(".modal-body").html('<img src="'+imageSrc + "screenshot" + node.getId() + ".jpg?nc="+nc + '">');
                $("#nodeModal").modal("show");
            });
            node.setImage(imageObj);
            ConnectionColorChange(stage,node.parent); //Include the stage and the group to enable again the interactivity with the nodes
            stage.draw();
        };
        var nc = new Date();
        nc = nc.getTime();
        imageObj.src = imageSrc + "screenshot" + node.getId() + ".jpg?nc="+nc;
        
    });       
    stage.draw();
       
}



/********************** AUXILIAR FUNCTION ****************/

function isNodeInserted(nodeId){
    var existNode = stage.get('#node'+nodeId);
    if (existNode.length > 0) {
        return true;
    }
    return false;
}

function initializeNode(data){

    //Obtain the data for each node 
    try{
        for(var i = 0; i < data.nodes.length; i++){
            var tempNode = data.nodes[i];
            var tempNodeObj = new NodeObj(tempNode.id,tempNode.name,tempNode.options,tempNode.type,tempNode.imgFile);
            for ( var j=0; j < tempNode.attributes.length; j++) {
                tempNodeObj.addAttribute(tempNode.attributes[j]);
            }
            nodeObjects.push(tempNodeObj);
        }
    }
    catch(err){
        //console.log("Error "+err.message);
        return
    }
    $('.element_list').bind('click',function(){        
        //Check if the node is already added
        var nodeExist = stage.get('#'+$(this).val());
        if(nodeExist.length == 0){
            //Request the node 
            //Change the class of the tag to identify that the node has been added
            $(this).toggleClass("element_list_activate");
            $(this).toggleClass("element_list");
            //increase initialPositionCounter
            initialPositionCounter++;
            //Genererate the Node by adding the group Node into the layer
            var nodeId = $(this).val();
            nodeObjTemp = getNodeId(nodeId);
            if ( nodeObjTemp.type == 2){
                layer.add(GenerateNode(stage,layer,0,$(this).val(),nodeObjTemp));
            }else{
                layer.add(GenerateNode(stage,layer,nodeObjTemp.options,$(this).val(),nodeObjTemp));
            }
            layer.draw();
        }
    });
}
/*******
    return true if the node initial and , at least, one ending node are inserted in the stage.
********/
function insertedEndInitNode(stage){
    var flagInitInserted = false;
    var flagEndInserted = false;
    nodes = stage.get('.node');
    nodes.each(function(node){
        if(node.getAttr("typeNode") == "1"){
            flagInitInserted = true;
        }else if(node.getAttr("typeNode") == "2"){
            flagEndInserted = true;
        }
    });
    return (flagInitInserted && flagEndInserted);
}
/***
    return true if all the connection are established otherwise return false
***/
function isAllConnected(stage){
    var flagConnection = true;
    connections = stage.get('.connection');
    connections.each(function(cnt){
        if(!cnt.getAttr("isConnected")){
            flagConnection = false;
        }
    });
    return flagConnection;
}

/**
   Check if the json exist, if exists then draw the stage with the json
**/
function printPreview(json){
    if (json == null){
        return -1;
    }
    stage = Kinetic.Node.create(json, 'canvas');
    //Layer to draw the labels for the nodes
    layer = stage.getChildren()[0];
    layer.draggable = false;
    //tooltipLayer = stage.getChildren()[1];
    AddEventsToPreview(stage,layer);
    layer.draggable = false;
    stage.draw();
}


