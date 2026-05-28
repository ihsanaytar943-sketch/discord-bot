const {
  Client,
  GatewayIntentBits,
  SlashCommandBuilder,
  REST,
  Routes,
  EmbedBuilder
} = require("discord.js");

// ================= CONFIG =================

const TOKEN = process.env.TOKEN;
const CLIENT_ID = process.env.CLIENT_ID;

// NUR DIESER CHANNEL
const ALLOWED_CHANNEL = "DEINE_CHANNEL_ID";

// ================= BOT =================

const client = new Client({
  intents: [GatewayIntentBits.Guilds]
});

// ================= COINS =================

const coins = new Map();

function getCoins(userId) {

  if (!coins.has(userId)) {
    coins.set(userId, 10000);
  }

  return coins.get(userId);
}

function addCoins(userId, amount) {

  coins.set(
    userId,
    getCoins(userId) + amount
  );
}

// ================= SYMBOLS =================

const symbols = [
  { icon: "🍋", multi: 2 },
  { icon: "🍒", multi: 3 },
  { icon: "🔔", multi: 5 },
  { icon: "BAR", multi: 10 },
  { icon: "7️⃣", multi: 25 }
];

function randomSymbol() {

  return symbols[
    Math.floor(Math.random() * symbols.length)
  ];
}

// ================= COMMANDS =================

const commands = [

  new SlashCommandBuilder()
    .setName("slot")
    .setDescription("🎰 3x3 Slotmaschine")
    .addIntegerOption(option =>
      option
        .setName("einsatz")
        .setDescription("Coins setzen")
        .setRequired(true)
    ),

  new SlashCommandBuilder()
    .setName("coins")
    .setDescription("💰 Zeigt deine Coins")

].map(c => c.toJSON());

// ================= REGISTER =================

const rest = new REST({
  version: "10"
}).setToken(TOKEN);

(async () => {

  try {

    console.log("Lade Commands...");

    await rest.put(
      Routes.applicationCommands(CLIENT_ID),
      { body: commands }
    );

    console.log("Commands geladen.");

  } catch (err) {

    console.error(err);

  }

})();

// ================= READY =================

client.once("ready", () => {

  console.log(`${client.user.tag} online`);

});

// ================= INTERACTION =================

client.on("interactionCreate", async interaction => {

  if (!interaction.isChatInputCommand()) return;

  // ================= CHANNEL CHECK =================

  if (interaction.channel.id !== ALLOWED_CHANNEL) {

    return interaction.reply({
      content: "❌ Der Bot funktioniert nur im Casino-Channel.",
      ephemeral: true
    });
  }

  // ================= COINS =================

  if (interaction.commandName === "coins") {

    return interaction.reply({
      content: `💰 Du hast ${getCoins(interaction.user.id)} Coins`,
      ephemeral: true
    });
  }

  // ================= SLOT =================

  if (interaction.commandName === "slot") {

    const bet = interaction.options.getInteger("einsatz");

    const userId = interaction.user.id;

    if (bet <= 0) {

      return interaction.reply({
        content: "❌ Ungültiger Einsatz.",
        ephemeral: true
      });
    }

    if (getCoins(userId) < bet) {

      return interaction.reply({
        content: "❌ Nicht genug Coins.",
        ephemeral: true
      });
    }

    // COINS ABZIEHEN
    addCoins(userId, -bet);

    await interaction.reply("🎰 Dreht...");

    // ANIMATION
    for (let i = 0; i < 5; i++) {

      const tempGrid = [];

      for (let row = 0; row < 3; row++) {

        let rowText = "";

        for (let col = 0; col < 3; col++) {

          rowText += randomSymbol().icon + " ";

        }

        tempGrid.push(rowText);
      }

      await new Promise(resolve =>
        setTimeout(resolve, 700)
      );

      await interaction.editReply({

        content:
`🎰 **SLOT MACHINE** 🎰

${tempGrid[0]}
${tempGrid[1]}
${tempGrid[2]}`

      });
    }

    // ================= FINAL GRID =================

    const grid = [];

    for (let row = 0; row < 3; row++) {

      const currentRow = [];

      for (let col = 0; col < 3; col++) {

        currentRow.push(randomSymbol());

      }

      grid.push(currentRow);
    }

    // ================= WIN CHECK =================

    const lines = [

      // horizontal
      [grid[0][0], grid[0][1], grid[0][2]],
      [grid[1][0], grid[1][1], grid[1][2]],
      [grid[2][0], grid[2][1], grid[2][2]],

      // diagonal
      [grid[0][0], grid[1][1], grid[2][2]],
      [grid[0][2], grid[1][1], grid[2][0]]
    ];

    let winnings = 0;

    for (const line of lines) {

      if (
        line[0].icon === line[1].icon &&
        line[1].icon === line[2].icon
      ) {

        winnings += bet * line[0].multi;
      }
    }

    // GEWINN GEBEN
    if (winnings > 0) {

      addCoins(userId, winnings);

    }

    // ================= FINAL GRID TEXT =================

    const finalGrid =
`${grid[0][0].icon} ${grid[0][1].icon} ${grid[0][2].icon}
${grid[1][0].icon} ${grid[1][1].icon} ${grid[1][2].icon}
${grid[2][0].icon} ${grid[2][1].icon} ${grid[2][2].icon}`;

    // ================= EMBED =================

    const embed = new EmbedBuilder()
      .setTitle("🎰 SLOT RESULT")
      .setDescription(finalGrid)
      .addFields(
        {
          name: "💰 Ergebnis",
          value:

            winnings > 0

              ? `🎉 Gewinn: ${winnings} Coins`

              : `❌ Verloren: ${bet} Coins`
        },
        {
          name: "🪙 Kontostand",
          value: `${getCoins(userId)} Coins`
        }
      )
      .setColor(

        winnings > 0

          ? "Gold"

          : "Red"
      );

    // ================= SEND =================

    await interaction.editReply({

      content: "",

      embeds: [embed]

    });
  }
});

// ================= LOGIN =================

client.login(TOKEN);
