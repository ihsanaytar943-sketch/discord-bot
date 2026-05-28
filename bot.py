const {
  Client,
  GatewayIntentBits,
  SlashCommandBuilder,
  REST,
  Routes,
  AttachmentBuilder,
  EmbedBuilder
} = require("discord.js");

const Canvas = require("canvas");
const GIFEncoder = require("gifencoder");
const fs = require("fs");

// ================= CONFIG =================

const TOKEN = process.env.TOKEN;
const CLIENT_ID = process.env.CLIENT_ID;

// ================= BOT =================

const client = new Client({
  intents: [GatewayIntentBits.Guilds]
});

// ================= COINSYSTEM =================

const coins = new Map();

function getCoins(userId) {

  if (!coins.has(userId)) {
    coins.set(userId, 10000);
  }

  return coins.get(userId);
}

function addCoins(userId, amount) {
  coins.set(userId, getCoins(userId) + amount);
}

// ================= SYMBOLS =================

const symbols = [
  {
    symbol: "🍋",
    multi: 1.5
  },
  {
    symbol: "🍒",
    multi: 2
  },
  {
    symbol: "🔔",
    multi: 5
  },
  {
    symbol: "BAR",
    multi: 10
  },
  {
    symbol: "7️⃣",
    multi: 25
  }
];

function randomSymbol() {

  return symbols[
    Math.floor(Math.random() * symbols.length)
  ];
}

// ================= COMMAND =================

const commands = [

  new SlashCommandBuilder()
    .setName("slot")
    .setDescription("🎰 Slot Machine")
    .addIntegerOption(option =>
      option
        .setName("einsatz")
        .setDescription("Wie viele Coins?")
        .setRequired(true)
    )

].map(command => command.toJSON());

// ================= DEPLOY =================

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

  } catch (error) {
    console.error(error);
  }

})();

// ================= READY =================

client.once("ready", () => {
  console.log(`${client.user.tag} online`);
});

// ================= SLOT =================

client.on("interactionCreate", async interaction => {

  if (!interaction.isChatInputCommand()) return;

  if (interaction.commandName !== "slot") return;

  const bet = interaction.options.getInteger("einsatz");

  const userId = interaction.user.id;

  // CHECKS
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

  await interaction.deferReply();

  // FINAL SYMBOLS
  const final1 = randomSymbol();
  const final2 = randomSymbol();
  const final3 = randomSymbol();

  // CANVAS
  const width = 400;
  const height = 250;

  const canvas = Canvas.createCanvas(width, height);

  const ctx = canvas.getContext("2d");

  // GIF
  const encoder = new GIFEncoder(width, height);

  const path = `slot-${userId}.gif`;

  encoder.createReadStream().pipe(
    fs.createWriteStream(path)
  );

  encoder.start();
  encoder.setRepeat(0);
  encoder.setDelay(70);
  encoder.setQuality(10);

  // ANIMATION
  for (let i = 0; i < 30; i++) {

    // BACKGROUND
    ctx.fillStyle = "#111";
    ctx.fillRect(0, 0, width, height);

    // TITLE
    ctx.fillStyle = "gold";
    ctx.font = "bold 35px Arial";

    ctx.fillText("🎰 SLOT", 120, 50);

    // BOXES
    ctx.fillStyle = "white";

    ctx.fillRect(40, 90, 90, 90);
    ctx.fillRect(155, 90, 90, 90);
    ctx.fillRect(270, 90, 90, 90);

    // SPIN EFFECT
    const s1 =
      i > 22
        ? final1.symbol
        : randomSymbol().symbol;

    const s2 =
      i > 25
        ? final2.symbol
        : randomSymbol().symbol;

    const s3 =
      i > 28
        ? final3.symbol
        : randomSymbol().symbol;

    // SYMBOLS
    ctx.fillStyle = "black";
    ctx.font = "50px Arial";

    ctx.fillText(s1, 60, 150);
    ctx.fillText(s2, 175, 150);
    ctx.fillText(s3, 290, 150);

    encoder.addFrame(ctx);
  }

  encoder.finish();

  // WIN CHECK
  let winnings = 0;

  if (
    final1.symbol === final2.symbol &&
    final2.symbol === final3.symbol
  ) {

    winnings = Math.floor(
      bet * final1.multi
    );

    addCoins(userId, winnings);
  }

  // EMBED
  const embed = new EmbedBuilder()
    .setTitle("🎰 SLOT RESULT")
    .setColor(
      winnings > 0
        ? "Gold"
        : "Red"
    )
    .setDescription(
      winnings > 0
        ? `🎉 Gewinn: ${winnings} Coins`
        : `❌ Verloren: ${bet} Coins`
    )
    .addFields({
      name: "💰 Kontostand",
      value: `${getCoins(userId)} Coins`
    });

  // SEND
  const attachment = new AttachmentBuilder(path);

  await interaction.editReply({
    embeds: [embed],
    files: [attachment]
  });

  // DELETE GIF
  setTimeout(() => {

    if (fs.existsSync(path)) {
      fs.unlinkSync(path);
    }

  }, 5000);

});

// ================= LOGIN =================

client.login(TOKEN);
