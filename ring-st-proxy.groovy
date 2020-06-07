/**
 * Simple switch to execute post request to python web
 * server that executes test_sound on Ring Chime
 */
metadata {
	definition (
      name: "Ring Doorbell Chime Proxy",
      namespace: "kmatt",
      author: "Kari Mattila") {
		capability "Actuator"
		capability "Switch"
		command "on"
		command "off"
	}

    preferences {
        input("host", "string", title:"IP", description: "The IP address and port of the Ring Proxy.", required: true, displayDuringSetup: true)
        input("chime", "string", title:"Chime", description: "What chime to play", required: true, displayDuringSetup: true)
	}

	tiles(scale:2) {
		multiAttributeTile(name:"controllerstatus", type: "generic", width: 6, height: 4) {
                        tileAttribute ("device.status", key: "PRIMARY_CONTROL") {
                        attributeState("online", label:'${name}', icon:"st.Home.home9", backgroundColor:"#79b821")
                        }
		}
                standardTile("on", "device.button", width: 2, height: 2) {
			state "default", label: "Turn On", backgroundColor: "#ffffff", action: "on", icon:""
		}
		standardTile("off", "device.button", width: 2, height: 2) {
			state "default", label: "Turn Off", backgroundColor: "#ffffff", action: "off", icon:""
		}
                details(["controllerstatus","on","off"])
	}
}

def parse(String description) {
	log.debug "Parsing '${description}'"
}

def getHostAddress() {
	return "${host}"
}

def on() {
	def cmds = []
	cmds << http_command("${chime}")
    log.debug cmds
	sendEvent(name: "on", value: "pushed", data: [buttonNumber: "1"], descriptionText: "$device.displayName Turn On was pushed", isStateChange: true)
    sendEvent(name: "switch", value: "on")
    return cmds
}

def off() {
	def cmds = []
	cmds << http_command("off")
    log.debug cmds
	sendEvent(name: "off", value: "pushed", data: [buttonNumber: "2"], descriptionText: "$device.displayName Turn Off was pushed", isStateChange: true)
	sendEvent(name: "switch", value: "off")
	return cmds
}

private http_command(chime) {
	log.debug("Playing chime " + chime + " through " + getHostAddress())

    def hubAction = new physicalgraph.device.HubAction(
        method: "POST",
        path: "/chime",
        headers: [
          HOST: getHostAddress(),
          "Content-Type": "application/json"
        ],
        body: "{\"kind\":\"" + chime + "\"}")

    return hubAction
}
