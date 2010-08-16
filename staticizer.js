function updatetestoutput()
	{
	var division = document.getElementById('willtestwith');
	var eightbitmask = 0xFF000000^0;

	var netmaskdecimal = (eightbitmask>>((document.forms[1].elements[5].value)-8));
	var ipaddrstring = (document.forms[1].elements[1].value+'.'+document.forms[1].elements[2].value+'.'+document.forms[1].elements[3].value+'.'+document.forms[1].elements[4].value);

	var ipaddrdecimal = quadtodec(ipaddrstring)&netmaskdecimal;
	division.innerHTML = String.prototype.concat('Script will run with IP Address: ', dectoquad(ipaddrdecimal), ' and Netmask: ', dectoquad(netmaskdecimal));
	}

function checkquad(object)
	{
	var localstring = object.value;
	var expression = /\D/g;
	object.value = localstring.replace(expression,'');
	if ((object.value < 1) || (object.value > 255))
		{
		object.value = object.defaultValue;
		}
	}

function quadtodec(ipaddr) //Expects a Quad
	{
	var ipstring = new String(ipaddr);
	var iparray = ipstring.split(".");
	var bitmask = 24;
	var returnvalue = 0;
	for (var i=0;i<4;i++)
		{
		returnvalue ^= iparray[i]<<bitmask;
		bitmask-=8;
		}
	return returnvalue;
	}


function dectoquad(decimal) //Expects a Decimal
	{
	var returnarray = new Array(4);
	var returnvalue = new String;
	var bitdepth = new Number(24);
	for (var i = 0; i < 4; i++)
		{
		var workingnum = decimal>>>bitdepth;
		returnarray[i] = workingnum;
		decimal-=(workingnum<<bitdepth);
		bitdepth-=8;
		}
	returnvalue=(returnarray[0]+"."+returnarray[1]+"."+returnarray[2]+"."+returnarray[3]);
	return returnvalue;
	}


function isSubnet(container, contained, netmask) //Expects Decimals
	{
	return ((container&netmask)==(contained&netmask));
	}

function findNextNet(startnet, netmask) //Expects Decimals, returns a decimal
	{
	var i=0;
	var newnet = new Number();
	while (i<25)
		{
		newnet = startnet+Math.pow(2,i++);
		if (!isSubnet(startnet,newnet,netmask)) return newnet;
		}
	return false;
	}

function findSurroundingNets(targetnetdecimal, targetnetmaskdecimal, division ) //Expects Decimals
	{
	// 134.65.0.0 is 0x86410000
	// 172.32.0.0 is 0xAC200000
	var lowerint = document.forms[0].elements[0].value;
	var higherint = document.forms[0].elements[1].value;
	var staticheader = String.prototype.concat('static (', lowerint, ',',higherint, ') ');
	var parentnet = new Array(2);
	
	if (isSubnet(0x86410000, targetnetdecimal, 0xFFFF0000))
		{
		parentnet[0] = 0x86410000^0; //134.65.0.0
		parentnet[1] = 0xFFFF0000^0; //255.255.0.0
		division.innerHTML+= String.prototype.concat(staticheader, '172.16.0.0 172.16.0.0 netmask 255.240.0.0<br />');
		}
	else if (isSubnet(0xAC100000^0, targetnetdecimal, 0xFFF00000^0))
		{
		parentnet[0] = 0xAC100000^0; //172.16.0.0
		parentnet[1] = 0xFFF00000^0; //255.240.0.0
		division.innerHTML+= String.prototype.concat(staticheader, '134.65.0.0 134.65.0.0 netmask 255.255.0.0<br />');
		}
	else
		{
		division.innerHTML+= String.prototype.concat(staticheader, '134.65.0.0 134.65.0.0 netmask 255.255.0.0<br />');
		division.innerHTML+= String.prototype.concat(staticheader, '172.16.0.0 172.16.0.0 netmask 255.240.0.0<br />');
		return false;
		}

	var upperparentbound = findNextNet(parentnet[0], parentnet[1]);

	while ( (parentnet[0] < targetnetdecimal) && (parentnet[1] <= targetnetmaskdecimal) )
		{
		while (isSubnet(parentnet[0], targetnetdecimal, parentnet[1]))
			{
			parentnet[1]>>=1;
			}
			division.innerHTML+= String.prototype.concat(staticheader, dectoquad(parentnet[0]), ' ', dectoquad(parentnet[0]), ' netmask ', dectoquad(parentnet[1]), '<br />');
		parentnet[0] = findNextNet(parentnet[0], parentnet[1]);
		}

	parentnet[0] = findNextNet(targetnetdecimal, targetnetmaskdecimal);

	while (parentnet[0] < upperparentbound)
		{
		parentnet[1] = 0xFFF00000^0; //255.240.0.0
		while ((isSubnet(parentnet[0], upperparentbound, parentnet[1])) || (isSubnet(parentnet[0], targetnetdecimal, parentnet[1])))
			{
			parentnet[1]>>=1;
			}
		parentnet[0]=parentnet[0]&parentnet[1];
		division.innerHTML+= String.prototype.concat(staticheader, dectoquad(parentnet[0]), ' ', dectoquad(parentnet[0]), ' netmask ', dectoquad(parentnet[1]), '<br />');
		parentnet[0] = findNextNet(parentnet[0], parentnet[1]);
		}
	}

