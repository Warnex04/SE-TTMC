<script>
  import { createEventDispatcher } from "svelte";
  import blockData from "./parsed_block_data.json";

  let blueprintFile = null;
  let unmatchedBlocks = [];
  let totalComponents = {};
  let blueprintSummary = null;

  const dispatch = createEventDispatcher(); // Create an event dispatcher

  function normalizeBlockName(name) {
    if (!name) return "";
    name = name.toLowerCase();
    name = name.replace("largeblock", "").replace("smallblock", "");
    name = name.replace("large", "").replace("small", "");
    name = name.replace(/[\s_]/g, "");
    return name;
  }

  async function processBlueprint() {
    if (!blueprintFile) {
      alert("Please select a blueprint file!");
      return;
    }

    const fileContent = await blueprintFile.text();
    const parser = new DOMParser();
    const xmlDoc = parser.parseFromString(fileContent, "application/xml");

    const blueprintBlocks = {};
    const unmatchedBlocksTemp = [];
    const totalComponentsTemp = {};

    const cubeBlocks = xmlDoc.getElementsByTagName("MyObjectBuilder_CubeBlock");

    for (let block of cubeBlocks) {
      const subtypeName =
        block.getElementsByTagName("SubtypeName")[0]?.textContent;
      if (subtypeName) {
        const normalizedName = normalizeBlockName(subtypeName);
        blueprintBlocks[normalizedName] =
          (blueprintBlocks[normalizedName] || 0) + 1;
      }
    }

    for (const [normalizedName, count] of Object.entries(blueprintBlocks)) {
      const matched = Object.keys(blockData).find((key) => {
        return normalizeBlockName(key) === normalizedName;
      });

      if (matched) {
        const components = blockData[matched]?.Large || [];
        for (const component of components) {
          const compName = component["Component Name"];
          const compCount = component["Component Count"] * count;
          totalComponentsTemp[compName] =
            (totalComponentsTemp[compName] || 0) + compCount;
        }
      } else {
        unmatchedBlocksTemp.push(normalizedName);
      }
    }

    blueprintSummary = {
      "Total unique block types": Object.keys(blueprintBlocks).length,
      "Total matched block types":
        Object.keys(blueprintBlocks).length - unmatchedBlocksTemp.length,
      "Total unmatched block types": unmatchedBlocksTemp.length,
      "Total component count": Object.values(totalComponentsTemp).reduce(
        (a, b) => a + b,
        0
      ),
    };

    unmatchedBlocks = unmatchedBlocksTemp;
    totalComponents = totalComponentsTemp;

    // Emit an event with the results
    dispatch("results", {
      blueprintSummary,
      unmatchedBlocks,
      totalComponents,
    });
  }
</script>

<div class="file-input-container">
  <label for="file-upload" class="custom-file-label">Choose File</label>
  <input
    type="file"
    id="file-upload"
    class="file-input"
    accept=".sbc"
    on:change="{(e) => (blueprintFile = e.target.files[0])}"
  />
  <span class="file-name">{blueprintFile ? blueprintFile.name : "No file chosen"}</span>
</div>

<style>
  .file-input-container {
    display: flex;
    align-items: center;
    gap: 10px;
  }

  .custom-file-label {
    display: inline-block;
    padding: 6px 12px;
    color: white;
    background-color: #803131;
    border: 2px solid #742929;
    border-radius: 4px;
    cursor: pointer;
    font-family: Arial, sans-serif;
    font-size: 0.9rem;
    text-align: center;
    transition: background-color 0.3s ease;
    padding: 0.5rem 1rem;
    margin: 20px 0 0 60px;
  }

  .custom-file-label:hover {
    background-color: #a04040;
  }

  .file-input {
    display: none; /* Hide the actual file input */
  }

  .file-name {
    font-family: Arial, sans-serif;
    font-size: 0.9rem;
    color: white;
  }
</style>