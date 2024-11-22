<script>
  let gravity = 1; // Default gravity in G
  let selectedGrid = "smallGrid"; // "smallGrid" or "largeGrid"
  let selectedOre = "emptyCargo"; // Default selected ore type
  let shipWeight = 0; // Total weight of the ship in tons
  let cargoInput = {
    small: { Vanilla: 0, Mk1: 0, Mk2: 0, Mk3: 0, Adv1: 0, Adv2: 0, Adv3: 0 },
    large: { Vanilla: 0, Mk1: 0, Mk2: 0, Mk3: 0, Adv1: 0, Adv2: 0, Adv3: 0 },
  };

  let totalMass = 0; // Total mass in tons
  let requiredForce = 0; // Required force in kN
  let thrustersRequired = {};
  let sliderValues = {}; // Store slider values for each tier (percentage of small thrusters)

  const baseThrust = {
    smallGrid: {
      smallThruster: 98.4, // in kN
      largeThruster: 480, // in kN
    },
    largeGrid: {
      smallThruster: 1080, // in kN
      largeThruster: 7200, // in kN
    },
  };

  const cargoMass = {
    smallGrid: {
      small: {
        Vanilla: 2.495,
        Mk1: 5,
        Mk2: 10,
        Mk3: 20,
        Adv1: 40,
        Adv2: 80,
        Adv3: 160,
      },
      large: {
        Vanilla: 312.5,
        Mk1: 625,
        Mk2: 1250,
        Mk3: 2500,
        Adv1: 5000,
        Adv2: 10000,
        Adv3: 20000,
      },
    },
    largeGrid: {
      small: {
        Vanilla: 312.5,
        Mk1: 625,
        Mk2: 1250,
        Mk3: 2500,
        Adv1: 5000,
        Adv2: 10000,
        Adv3: 20000,
      },
      large: {
        Vanilla: 8437.5,
        Mk1: 16875,
        Mk2: 33750,
        Mk3: 67500,
        Adv1: 135000,
        Adv2: 270000,
        Adv3: 540000,
      },
    },
  };

  const oreDensity = {
    NoOre: {
      empty: 0,
    },
    lowQuality: {
      iron: 0.27,
      silicon: 0.27,
      silver: 0.27,
      malachite: 0.27,
      lateryte: 0.27,
      palladium: 0.27,
    },
    mediumQuality: {
      cobalt: 0.37,
      nickel: 0.37,
    },
    ice: 0.5,
  };

  $: {
    calculate();
    gravity;
    cargoInput;
    sliderValues;
    shipWeight;
    selectedGrid;
    selectedOre;
  }

  function calculate() {
    totalMass = shipWeight; // Start with ship weight

    // If the "Empty Cargo" option is selected, skip cargo calculation
    if (selectedOre !== "emptyCargo") {
      let density;
      if (selectedOre === "ice") {
        density = oreDensity.ice;
      } else if (selectedOre in oreDensity.lowQuality) {
        density = oreDensity.lowQuality[selectedOre];
      } else if (selectedOre in oreDensity.mediumQuality) {
        density = oreDensity.mediumQuality[selectedOre];
      }

      // Calculate total mass for small and large blocks separately
      for (const blockType in cargoInput) {
        const massData = cargoMass[selectedGrid][blockType];
        for (const tier in cargoInput[blockType]) {
          totalMass += cargoInput[blockType][tier] * massData[tier] * density;
        }
      }
    }

    // Calculate required force
    requiredForce = totalMass * gravity * 9.8;

    // Calculate thrusters required for each tier
    thrustersRequired = {};
    for (const tier of Object.keys(cargoInput.small)) {
      const smallThrust = baseThrust[selectedGrid].smallThruster;
      const largeThrust = baseThrust[selectedGrid].largeThruster;
      const split = sliderValues[tier] || 0; // Default split is 0%

      let smallShare = split / 100;
      let largeShare = 1 - smallShare;

      const forceForSmall = requiredForce * smallShare;
      const forceForLarge = requiredForce * largeShare;

      const forcePerSmall =
        smallThrust * Math.pow(2, parseInt(tier.slice(2)) || 0);
      const forcePerLarge =
        largeThrust * Math.pow(2, parseInt(tier.slice(2)) || 0);

      thrustersRequired[tier] = {
        small: Math.ceil(forceForSmall / forcePerSmall),
        large: Math.ceil(forceForLarge / forcePerLarge),
      };
    }
  }
</script>

<main>
  <h1>Space Engineers: Cargo and Thruster Calculator</h1>

  <!-- Grid Selection -->
  <section>
    <h2>Grid Selection</h2>
    <label for="grid">Select Grid Type:</label>
    <select id="grid" bind:value={selectedGrid}>
      <option value="smallGrid">Small Grid</option>
      <option value="largeGrid">Large Grid</option>
    </select>

    <h2>Cargo Inputs</h2>

    <div class="cargo-container">
      <!-- Small Cargo Inputs -->
      <div class="cargo-input-group">
        <h3>Small Block</h3>
        {#each Object.keys(cargoInput.small) as tier}
          <label for={`cargo-small-${tier}`}>Cargo ({tier}):</label>
          <input
            id={`cargo-small-${tier}`}
            type="number"
            bind:value={cargoInput.small[tier]}
            min="0"
            step="1"
          />
        {/each}
      </div>

      <!-- Large Cargo Inputs -->
      <div class="cargo-input-group">
        <h3>Large Block</h3>
        {#each Object.keys(cargoInput.large) as tier}
          <label for={`cargo-large-${tier}`}>Cargo ({tier}):</label>
          <input
            id={`cargo-large-${tier}`}
            type="number"
            bind:value={cargoInput.large[tier]}
            min="0"
            step="1"
          />
        {/each}
      </div>
    </div>
  </section>

  <section>
    <h2>Enter Gravity</h2>

    <!-- Gravity Input -->
    <label for="gravity">Gravity (G):</label>
    <input
      id="gravity"
      type="number"
      bind:value={gravity}
      min="0.1"
      step="0.1"
    />

    <!-- Ship Weight Input -->
    <label for="shipWeight">Ship Weight (Tons):</label>
    <input
      id="shipWeight"
      type="number"
      bind:value={shipWeight}
      min="0"
      step="0.1"
    />

    <!-- Ore Selection -->
    <h3>Select Ore Type</h3>
    <ul>
      <li>
        <label>
          <input
            type="radio"
            name="ore"
            value="emptyCargo"
            bind:group={selectedOre}
          />
          Empty Cargo
        </label>
      </li>
      <li>
        <label>
          <input
            type="radio"
            name="ore"
            value="iron"
            bind:group={selectedOre}
          />
          Low Quality: Iron
        </label>
      </li>
      <li>
        <label>
          <input
            type="radio"
            name="ore"
            value="cobalt"
            bind:group={selectedOre}
          />
          Medium Quality: Cobalt
        </label>
      </li>
      <li>
        <label>
          <input type="radio" name="ore" value="ice" bind:group={selectedOre} />
          Ice
        </label>
      </li>
    </ul>
  </section>

  <!-- Cargo Inputs -->
  <section>
    <h2>Results</h2>
    <p><strong>Total Mass:</strong> {totalMass.toFixed(2)} T</p>
    <p><strong>Required Force:</strong> {requiredForce.toFixed(2)} kN</p>

    <table>
      <thead>
        <tr>
          <th>Tier</th>
          <th>Split (%)</th>
          <th>Small Thrusters</th>
          <th>Large Thrusters</th>
        </tr>
      </thead>
      <tbody>
        {#each Object.keys(thrustersRequired) as tier}
          <tr>
            <td>{tier}</td>
            <td>
              <input
                type="range"
                min="0"
                max="100"
                step="1"
                bind:value={sliderValues[tier]}
                class="draggable-number"
              />
              <span>{sliderValues[tier]}%</span>
            </td>
            <td>{thrustersRequired[tier].small}</td>
            <td>{thrustersRequired[tier].large}</td>
          </tr>
        {/each}
      </tbody>
    </table>
  </section>
</main>

<footer>
  <p>
    Made with <span class="green-heart">💚</span> by <strong>Warnex</strong>
    | <a href="https://github.com/Warnex04" target="_blank">GitHub</a>
  </p>
</footer>

<style>
  main {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
    font-family: Arial, sans-serif;
    margin: 0 auto;
    max-width: 1200px;
    text-align: center;
  }

  section {
    border: 2px solid #381313;
    border-radius: 8px;
    padding: 10px;
    background-color: #110606;
  }

  table {
    width: 100%;
    border-collapse: separate;
    margin-top: 10px;
  }

  th,
  td {
    border: 1px solid #742929;
    padding: 5px;
  }

  th {
    background-color: #803131;
  }

  td {
    background-color: #1f0606;
  }

  h1 {
    grid-column: span 3;
  }

  label {
    display: block;
    font-size: 0.9em;
    margin-bottom: 5px;
  }

  input {
    width: 20%;
    padding: 4px;
    border-radius: 10%;
    margin-bottom: 5px;
    text-align: center;
  }

  select {
    width: 70%;
    padding: 5px;
    border-radius: 5px;
    border: 1px solid #742929;
    background-color: #1f0606;
    color: white;
    text-align: center;
  }

  .cargo-container {
    display: flex;
    justify-content: space-between;
    gap: 20px;
  }

  .cargo-input-group {
    flex: 1;
    border: 2px solid #381313;
    border-radius: 8px;
    padding: 10px;
    background-color: #110606;
  }

  .cargo-input-group h3 {
    text-align: center;
    color: #ffffff;
  }

  .cargo-input-group label {
    display: block;
    margin-top: 10px;
    color: #ffffff;
  }

  .cargo-input-group input {
    width: 70%;
    padding: 5px;
    border-radius: 4px;
    background-color: #1f0606;
    color: #ffffff;
    border: 1px solid #742929;
    text-align: center;
  }

  section input[type="number"] {
    width: 70%;
    padding: 5px;
    border-radius: 5px;
    border: 1px solid #742929;
    background-color: #1f0606;
    color: white;
    text-align: center;
  }

  /* Styling for ore radio buttons */
  section ul {
    margin: 10px 0 0 20px;
    padding: 0;
    color: transparent;
    text-align: left;
  }

  section li {
    margin-bottom: 5px;
  }

  section label {
    color: white;
  }

  /* Styling the range input */
  table input[type="range"].draggable-number {
    -webkit-appearance: none; /* Remove default styling */
    appearance: none;
    width: 150px; /* Adjust width for usability */
    height: 6px;
    background: #742929; /* Background color for the track */
    border-radius: 3px;
    outline: none;
    margin-right: 10px; /* Space between range and percentage */
    cursor: pointer;
  }

  /* Thumb (draggable circle) styling */
  table input[type="range"].draggable-number::-webkit-slider-thumb {
    -webkit-appearance: none;
    appearance: none;
    width: 16px; /* Width of the thumb */
    height: 16px; /* Height of the thumb */
    background: #803131; /* Color of the thumb */
    border: 2px solid #1f0606;
    border-radius: 50%; /* Make it circular */
    cursor: pointer;
  }

  table input[type="range"].draggable-number::-moz-range-thumb {
    width: 16px;
    height: 16px;
    background: #803131;
    border: 2px solid #1f0606;
    border-radius: 50%;
    cursor: pointer;
  }

  table input[type="range"].draggable-number::-ms-thumb {
    width: 16px;
    height: 16px;
    background: #803131;
    border: 2px solid #1f0606;
    border-radius: 50%;
    cursor: pointer;
  }

  footer {
    margin-top: 20px;
    text-align: center;
    font-size: 1rem;
    color: white;
  }

  footer p {
    margin: 0;
  }

  .green-heart {
    color: #32cd32;
  }
</style>
