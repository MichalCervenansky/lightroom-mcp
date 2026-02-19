-- TestCommandHandlers.lua
-- Unit tests for CommandHandlers.lua using Mocks

-- Load Mocks
local Mocks = require 'Mocks'

-- Load CommandHandlers (it will use the global 'import' from Mocks)
local CommandHandlers = dofile("../CommandHandlers.lua")

-- Test Helpers
local function assertEqual(expected, actual, msg)
    if expected ~= actual then
        error(msg or string.format("Expected %s, got %s", tostring(expected), tostring(actual)))
    end
end

local function assertTable(t, msg)
    if type(t) ~= "table" then
         error(msg or "Expected table, got " .. type(t))
    end
end


-- Tests
local Tests = {}

function Tests.test_get_studio_info()
    print("Running test_get_studio_info...")
    local result = CommandHandlers.get_studio_info({})
    assertTable(result)
    assertEqual("Test Catalog", result.catalogName)
    assertEqual("0.1.0", result.pluginVersion)
    print("PASS")
end

function Tests.test_get_selection_empty()
    print("Running test_get_selection_empty...")
    Mocks.state.photos = {} -- Clear selection
    local result = CommandHandlers.get_selection({})
    assertTable(result)
    assertTable(result.photos)
    assertEqual(0, #result.photos)
    print("PASS")
end

function Tests.test_get_selection_populated()
    print("Running test_get_selection_populated...")
    local p1 = Mocks.Photo.new("123", "test.jpg")
    p1:setRawMetadata("rating", 3)
    Mocks.state.photos = { p1 }

    local result = CommandHandlers.get_selection({})
    assertTable(result)
    assertEqual(1, #result.photos)
    assertEqual("123", result.photos[1].localId)
    assertEqual(3, result.photos[1].rating)
    print("PASS")
end

function Tests.test_set_rating()
    print("Running test_set_rating...")
    local p1 = Mocks.Photo.new("123", "test.jpg")
    Mocks.state.photos = { p1 }

    -- Valid rating
    local result = CommandHandlers.set_rating({ rating = 5 })
    assertTable(result)
    assertEqual(true, result.success)
    assertEqual(5, p1:getRawMetadata("rating"))

    -- Invalid rating
    result = CommandHandlers.set_rating({ rating = 6 })
    assertTable(result)
    assertEqual("Rating must be between 0 and 5", result.error)
    print("PASS")
end

function Tests.test_add_to_collection()
    print("Running test_add_to_collection...")
    local p1 = Mocks.Photo.new("123", "test.jpg")
    Mocks.state.photos = { p1 }
    Mocks.state.collections = {}

    local result = CommandHandlers.add_to_collection({ collectionName = "My Collection" })
    assertTable(result)
    assertEqual(true, result.success)

    assertEqual(1, #Mocks.state.collections)
    assertEqual("My Collection", Mocks.state.collections[1]:getName())
    assertEqual(1, #Mocks.state.collections[1].photos)
    print("PASS")
end


-- Run Runner
local function run()
    local passed = 0
    local failed = 0

    for name, func in pairs(Tests) do
        local status, err = pcall(func)
        if status then
            passed = passed + 1
        else
            print("FAIL: " .. name .. " - " .. err)
            failed = failed + 1
        end
    end

    print(string.format("\nResults: %d Passed, %d Failed", passed, failed))
    if failed > 0 then os.exit(1) end
end

run()
