-- Mocks.lua
-- Mocks for Lightroom SDK globals to run tests outside of Lightroom

local Mocks = {}

-- Global table to hold mock state
Mocks.state = {
    catalog = nil,
    photos = {},
    collections = {},
    keywords = {}
}

-- helper to split string
function string.split(inputstr, sep)
    if sep == nil then sep = "%s" end
    local t={}
    for str in string.gmatch(inputstr, "([^"..sep.."]+)") do
        table.insert(t, str)
    end
    return t
end

-- Mock import function
function import( name )
    if name == 'LrApplication' then return Mocks.LrApplication end
    if name == 'LrApplicationView' then return Mocks.LrApplicationView end
    if name == 'LrSelection' then return Mocks.LrSelection end
    if name == 'LrLogger' then return Mocks.LrLogger end
    if name == 'LrTasks' then return Mocks.LrTasks end
    if name == 'LrFunctionContext' then return Mocks.LrFunctionContext end
    if name == 'LrPathUtils' then return Mocks.LrPathUtils end
    if name == 'LrFileUtils' then return Mocks.LrFileUtils end
    return {}
end

-- Mock LrLogger
Mocks.LrLogger = function( name )
    return {
        enable = function() end,
        trace = function( self, msg ) print("TRACE: " .. tostring(msg)) end,
        debug = function( self, msg ) print("DEBUG: " .. tostring(msg)) end,
        info = function( self, msg ) print("INFO: " .. tostring(msg)) end,
        warn = function( self, msg ) print("WARN: " .. tostring(msg)) end,
        error = function( self, msg ) print("ERROR: " .. tostring(msg)) end,
    }
end

-- Mock LrTasks
Mocks.LrTasks = {
    pcall = function( func, ... )
        return pcall( func, ... )
    end,
    startAsyncTask = function( func )
        func()
    end,
    sleep = function() end,
    yield = function() end
}

-- Mock LrFunctionContext
Mocks.LrFunctionContext = {
    callWithContext = function( name, func )
        func( {} )
    end
}

-- Mock Photo Class
Mocks.Photo = {}
Mocks.Photo.__index = Mocks.Photo

function Mocks.Photo.new( id, filename )
    local self = setmetatable( {}, Mocks.Photo )
    self.localIdentifier = id
    self.metadata = {
        fileName = filename,
        path = "/path/to/" .. filename,
        rating = 0,
        colorNameForLabel = nil,
        title = "",
        caption = "",
        pickStatus = 0,
        keywords = {}
    }
    return self
end

function Mocks.Photo:getRawMetadata( key )
    return self.metadata[key]
end

function Mocks.Photo:getFormattedMetadata( key )
    return self.metadata[key]
end

function Mocks.Photo:setRawMetadata( key, value )
    self.metadata[key] = value
end

function Mocks.Photo:addKeyword( keyword )
    table.insert( self.metadata.keywords, keyword )
end
function Mocks.Photo:removeKeyword( keyword )
    -- remove by name matching for simplicity
     for i, kw in ipairs(self.metadata.keywords) do
        if kw:getName() == keyword:getName() then
            table.remove(self.metadata.keywords, i)
            break
        end
    end
end


-- Mock Collection Class
Mocks.Collection = {}
Mocks.Collection.__index = Mocks.Collection

function Mocks.Collection.new( name, id )
    local self = setmetatable( {}, Mocks.Collection )
    self.name = name
    self.localIdentifier = id
    self.photos = {}
    return self
end

function Mocks.Collection:getName() return self.name end
function Mocks.Collection:addPhotos( photos )
    for _, p in ipairs(photos) do
        table.insert(self.photos, p)
    end
end
function Mocks.Collection:getChildCollections() return {} end
function Mocks.Collection:getChildCollectionSets() return {} end


-- Mock Keyword Class
Mocks.Keyword = {}
Mocks.Keyword.__index = Mocks.Keyword
function Mocks.Keyword.new(name, parent)
    local self = setmetatable({}, Mocks.Keyword)
    self.name = name
    self.parent = parent
    self.children = {}
    return self
end
function Mocks.Keyword:getName() return self.name end
function Mocks.Keyword:getParent() return self.parent end
function Mocks.Keyword:getChildren() return self.children end

-- Mock Catalog
Mocks.Catalog = {
    getPath = function() return "C:\\Users\\Test\\Pictures\\Lightroom\\Test Catalog.lrcat" end,
    getTargetPhoto = function() return Mocks.state.photos[1] end,
    getTargetPhotos = function() return Mocks.state.photos end,
    getAllPhotos = function() return Mocks.state.photos end,
    withWriteAccessDo = function( self, name, func )
        func( {} )
    end,
    getKeywords = function() return Mocks.state.keywords end,
    createKeyword = function(self, name, parent)
        local kw = Mocks.Keyword.new(name, parent)
        if parent then
            table.insert(parent.children, kw)
        else
            table.insert(Mocks.state.keywords, kw)
        end
        return kw
    end,
    getChildCollections = function() return Mocks.state.collections end,
    getChildCollectionSets = function() return {} end,
    createCollection = function(self, name, parent, isSmart)
        local c = Mocks.Collection.new(name, "col-"..name)
        table.insert(Mocks.state.collections, c)
        return c
    end
}

-- Mock LrApplication
Mocks.LrApplication = {
    activeCatalog = function() return Mocks.Catalog end
}

return Mocks
