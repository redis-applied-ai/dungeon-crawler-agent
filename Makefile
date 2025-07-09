# Inform compiler paths (can be overridden via environment variables)
INFORM_APP ?= /Applications/Inform.app
INFORM_NI_BIN ?= $(INFORM_APP)/Contents/MacOS/ni
INFORM_BIN = 
INFORM_INTERNAL ?= $(INFORM_APP)/Contents/Resources/Internal

# User-specific paths (can be overridden via environment variables)
INFORM_EXTERNAL ?= $(HOME)/Library/Inform
PROJECT_PATH ?= $(shell pwd)/src/dungeon/Clockwork.inform
OUTPUT_FORMAT ?= ulx
OUTPUT_FILE ?= $(shell pwd)/games/dungeon.$(OUTPUT_FORMAT)

# Set the inform6 flags and output file based on format
ifeq ($(OUTPUT_FORMAT),z8)
	INFORM6_FLAGS = -kE2SDwv8
	INFORM6_OUTPUT = output.z8
else ifeq ($(OUTPUT_FORMAT),ulx)
	INFORM6_FLAGS = -kE2SDG
	INFORM6_OUTPUT = output.ulx
else
	$(error Unsupported OUTPUT_FORMAT: $(OUTPUT_FORMAT). Use z8 or ulx)
endif

.PHONY: build clean

build:
	sed -i '' 's/    /\t/g' $(PROJECT_PATH)/Source/story.ni
	$(INFORM_NI_BIN) "-internal" "$(INFORM_INTERNAL)" "-external" "$(INFORM_EXTERNAL)" "-project" "$(PROJECT_PATH)" "-format=$(OUTPUT_FORMAT)"
	$(INFORM_APP)/Contents/MacOS/inform6 $(INFORM6_FLAGS) +include_path=/Applications/Inform.app/Contents/Resources/Library/6.11,.,../Source $(PROJECT_PATH)/Build/auto.inf $(PROJECT_PATH)/Build/$(INFORM6_OUTPUT)
	cp $(PROJECT_PATH)/Build/$(INFORM6_OUTPUT) $(OUTPUT_FILE)
	@echo "Built $(OUTPUT_FILE)"

clean:
	rm -f $(OUTPUT_FILE)
