local LrApplication = import 'LrApplication'
local LrSelection = import 'LrSelection'
local LrLogger = import 'LrLogger'

local logger = LrLogger( 'MCPBridge' )

local CommandHandlers = {}

function CommandHandlers.get_studio_info( params )
    local catalog = LrApplication.activeCatalog()
    return {
        catalogName = catalog:getName(),
        catalogPath = catalog:getPath(),
        -- LrApplication doesn't easily give version string in all SDKs, but we can return static info
        pluginVersion = "0.1.0"
    }
end

function CommandHandlers.get_selection( params )
    local catalog = LrApplication.activeCatalog()
    local targetPhotos = catalog:getTargetPhotos()
    
    local result = {}
    for _, photo in ipairs( targetPhotos ) do
        table.insert( result, {
            localId = photo.localIdentifier,
            filename = photo:getFormattedMetadata( 'fileName' ),
            path = photo:getRawMetadata( 'path' ),
            rating = photo:getRawMetadata( 'rating' ),
            label = photo:getRawMetadata( 'label' ),
            title = photo:getFormattedMetadata( 'title' ),
            caption = photo:getFormattedMetadata( 'caption' )
        } )
    end
    
    return { photos = result }
end

function CommandHandlers.set_metadata( params )
    local catalog = LrApplication.activeCatalog()
    local targetPhotos = catalog:getTargetPhotos() -- Or find by ID if provided in params
    
    -- If params has specific photo IDs, logic would be more complex.
    -- For now, act on selection.
    
    local success = false
    local err = nil
    
    catalog:withWriteAccessDo( "MCP Set Metadata", function( context )
        for _, photo in ipairs( targetPhotos ) do
            if params.rating then
                photo:setRawMetadata( 'rating', params.rating )
            end
            if params.label then
                photo:setRawMetadata( 'label', params.label )
            end
            if params.title then
                photo:setRawMetadata( 'title', params.title )
            end
            if params.caption then
                photo:setRawMetadata( 'caption', params.caption )
            end
        end
        success = true
    end )
    
    return { success = success }
end

return CommandHandlers
