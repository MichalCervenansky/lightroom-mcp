local JSON = require 'JSON' -- Need to verify if LrC has built-in JSON or if we need a library. 
-- LrC SDK has 'LrJson' in older versions or often plugins bundle `json.lua`.
-- Actually, LrC SDK usually does NOT include a global JSON library accessible this way. 
-- We often use a pure lua JSON library.
-- Checking assumptions: standard Lr SDK does not have `require 'JSON'`.
-- We will need to include a JSON library. For now, I'll assume we can use `dkjson` or similar, 
-- but since I can't easily npm install into Lua, I should create a simple JSON.lua or find one.
-- WAIT, `import 'LrXml'` exists, effectively.
-- Let's try to write a simple JSON dump/parse or use a known one. 
-- To be safe, I will create a `JSON.lua` file which is a standard dkjson or json.lua implementation.

local LrLogger = import 'LrLogger'
local JSON = require 'JSON'
local CommandHandlers = require 'CommandHandlers'

local logger = LrLogger( 'MCPBridge' )

local function logToFile( msg )
    local path = "D:\\Projects\\lightroom-mcp\\plugin_debug.log"
    local f = io.open( path, "a" )
    if f then
        f:write( os.date() .. " [Server]: " .. tostring(msg) .. "\n" )
        f:close()
    end
end

local Server = {}

function Server.start( context )
    logToFile( "Starting Server on port 54321..." )
    
    local serverSocket = LrSocket.bind {
        functionContext = context,
        port = 54321,
        mode = "text",
        onConnected = function( socket, port )
            logToFile( "Client connected from " .. tostring(port) )
            
            socket:setReceiver( function( socket, message )
                logToFile( "Received: " .. message )
                
                local response = { jsonrpc = "2.0", id = nil }
                
                local status, request = pcall( JSON.decode, message )
                
                if not status or not request then
                    logToFile("JSON Decode Error: " .. tostring(request))
                    response.error = { code = -32700, message = "Parse error" }

                else
                    response.id = request.id
                    local handler = CommandHandlers[ request.method ]
                    
                    if handler then
                        local success, result = pcall( handler, request.params )
                        if success then
                            response.result = result
                        else
                            response.error = { code = -32603, message = "Internal error", data = result }
                        end
                    else
                        response.error = { code = -32601, message = "Method not found" }
                    end
                end
                
                local responseStr = JSON.encode( response )
                socket:send( responseStr .. "\n" )
            end )
            
            socket:onClosed( function( socket )
                logger:trace( "Client disconnected" )
            end )
        end,
        onError = function( socket, err )
            logToFile( "Server socket error: " .. tostring(err) )
        end
    }
    
    if serverSocket then
       logToFile( "Server bound successfully." )
       while true do
           LrTasks.sleep( 1 )
       end
    else
        logToFile( "Failed to bind port 54321" )
    end
end

return Server
