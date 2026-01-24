local LrTasks = import 'LrTasks'
local LrSocket = import 'LrSocket'
local LrFunctionContext = import 'LrFunctionContext'
local LrLogger = import 'LrLogger'
local LrPathUtils = import 'LrPathUtils'
local LrFileUtils = import 'LrFileUtils'

local logger = LrLogger( 'MCPBridge' )
logger:enable( 'print' ) 

-- Debug file logger
local function logToFile( msg )
    local path = "D:\\Projects\\lightroom-mcp\\plugin_debug.log"
    local f = io.open( path, "a" )
    if f then
        f:write( os.date() .. ": " .. tostring(msg) .. "\n" )
        f:close()
    end
end

logToFile("Init.lua: Loading...")

local status, Server = pcall( require, 'Server' )
if not status then
    logToFile("Init.lua: Failed to require Server: " .. tostring(Server))
    return
end

LrTasks.startAsyncTask( function()
    logToFile( "Init.lua: Task started" )
    
    LrFunctionContext.callWithContext( 'MCPServer', function( context )
        logToFile( "Init.lua: Calling Server.start" )
        local success, err = pcall( Server.start, context )
        if not success then
            logToFile( "Init.lua: Server.start crashed: " .. tostring(err) )
        else
            logToFile( "Init.lua: Server.start returned (unexpected if loop exists)" )
        end
    end )
    
    logToFile( "Init.lua: Task ended" )
end )
