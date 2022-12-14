use std::collections::HashMap;
use std::env;
use std::sync::Arc;

use serenity::async_trait;
use serenity::framework::standard::macros::{command, group};
use serenity::framework::standard::{CommandResult, StandardFramework};
use serenity::model::channel::Message;
use serenity::model::prelude::{GuildId, Reaction, ReactionType, UserId};
use serenity::prelude::*;

use lazy_static::lazy_static;

#[group]
#[commands(help, map, remap, delete)]
struct General;

struct Handler;

type ServerMap = HashMap<GuildId, HashMap<String, String>>;

lazy_static! {
    static ref HASHMAP: Arc<Mutex<ServerMap>> = {
        let try_bytes = std::fs::read("db/map.ron");
        let bytes = match &try_bytes {
            Ok(bytes) => bytes.clone(),
            Err(_err) => {
                let _ = std::fs::write("db/map.ron", "");
                vec!['{' as u8, '}' as u8]
            }
        };

        let map = ron::de::from_bytes(&bytes).expect("Could not parse input");

        let mutex = Mutex::new(map);
        Arc::new(mutex)
    };
}

async fn check_mapping_exist(gid: &GuildId, id: &str) -> bool {
    let server_hashmap = HASHMAP.lock().await;
    let hashmap = server_hashmap.get(gid);

    match hashmap {
        Some(hashmap) => hashmap.get(id).is_some(),
        None => false,
    }
}

fn check_command(command: Option<&str>, expect: &str) -> bool {
    command.is_some() && command.unwrap() == expect
}

macro_rules! get_content {
    ($args:ident, $msg:ident, $ctx:ident, $text :literal) => {{
        let content = $args.collect::<Vec<_>>();
        if content.len() == 0 {
            const MESSAGE: &str = concat!("Missing content. `Usage: !!", $text, " <id> <content>`");
            dbg!(&MESSAGE);
            let _ = $msg.reply(&$ctx, MESSAGE).await;
            return Ok(());
        }

        content.join(" ")
    }};
}

macro_rules! get_id {
    ($args:ident, $msg:ident, $ctx:ident, $text:literal) => {{
        get_id!($args, $msg, $ctx, $text, true)
    }};

    ($args:ident, $msg:ident, $ctx:ident, $text:literal, $is_content:literal) => {{
        let id = $args.next();
        if id.is_none() {
            const MESSAGE: &str = if $is_content {
                concat!("Missing identifier. `Usage: !!", $text, " <id> <content>`")
            } else {
                concat!("Missing identifier. `Usage: !!", $text, " <id>`")
            };
            let _ = $msg.reply(&$ctx, MESSAGE).await;
            return Ok(());
        }

        id.unwrap()
    }};
}

macro_rules! get_guild {
    ($msg: ident, $ctx: ident) => {
        match $msg.guild_id {
            Some(guild) => guild,
            None => {
                const MESSAGE: &str = "Message was not from a discord server";
                dbg!(&MESSAGE);
                let _ = $msg.reply(&$ctx, MESSAGE).await;
                return Ok(());
            }
        }
    };
}

#[async_trait]
impl EventHandler for Handler {
    async fn message(&self, ctx: Context, msg: Message) {
        if !msg.content.starts_with("!!") {
            return;
        }

        let guild_id = match msg.guild_id {
            Some(guild) => guild,
            None => {
                const MESSAGE: &str = "Message was not from a discord server";
                dbg!(&MESSAGE);
                let _ = msg.reply(&ctx, MESSAGE).await;
                return;
            }
        };

        // Handle identifiers
        let mut options = msg.content.split("!!").skip(1);

        let command = options.next();
        if command.is_none() {
            return;
        }

        let command = command.unwrap().trim();

        let server_hashmap = HASHMAP.lock().await;
        let hashmap = server_hashmap.get(&guild_id);

        let value = match hashmap {
            Some(hashmap) => hashmap.get(command),
            None => None,
        };

        match value {
            Some(message) => {
                let tmp = msg.reply(&ctx, message).await;

                if let Ok(message) = tmp {
                    let _ = message
                        .react(&ctx, ReactionType::Unicode(String::from("🗑️")))
                        .await;
                }
            }
            None => (),
        };
    }

    async fn reaction_add(&self, ctx: Context, reaction: Reaction) {
        let message = reaction.message(&ctx).await.unwrap();
        let user = message.author.id;

        const BOT_ID: UserId = UserId(819549623172726824);

        if user != BOT_ID {
            return;
        }

        if reaction.emoji == ReactionType::Unicode(String::from("🗑️"))
            && reaction.user_id != Some(BOT_ID)
        {
            let _ = message.delete(&ctx).await;
        }
    }
}

#[tokio::main]
async fn main() {
    let framework = StandardFramework::new()
        .configure(|c| c.prefix("!!")) // set the bot's prefix to "!!"
        .group(&GENERAL_GROUP);

    // Login with a bot token from the environment
    let token = env::var("DISCORD_TOKEN").expect("token");
    let intents = GatewayIntents::non_privileged() | GatewayIntents::MESSAGE_CONTENT;
    let mut client = Client::builder(token, intents)
        .event_handler(Handler)
        .framework(framework)
        .await
        .expect("Error creating client");

    // start listening for events by starting a single shard
    if let Err(why) = client.start().await {
        println!("An error occurred while running the client: {:?}", why);
    }
}

#[command]
async fn ping(ctx: &Context, msg: &Message) -> CommandResult {
    msg.reply(ctx, "Pong!").await?;

    Ok(())
}

#[command]
async fn remap(ctx: &Context, msg: &Message) -> CommandResult {
    let guild_id = get_guild!(msg, ctx);

    let mut options = msg.content.split(' ');
    if !check_command(options.next(), "!!remap") {
        return Ok(());
    }

    // Get id
    let id = get_id!(options, msg, ctx, "remap");
    if !check_mapping_exist(&guild_id, id).await {
        const MESSAGE: &str = "Identifier doesn't exist. `Usage: !!map <id> <content>`";
        dbg!(&MESSAGE);
        let _ = msg.reply(&ctx, MESSAGE).await;
        return Ok(());
    }

    let content = get_content!(options, msg, ctx, "remap");
    let message = format!("Remapped `!!{id}` to `{content}`. You can use `!!{id}`");

    let mut server_hashmap = HASHMAP.lock().await;
    let hashmap = server_hashmap.get_mut(&guild_id);
    match hashmap {
        Some(hashmap) => {
            hashmap.insert(String::from(id), content);
        }
        None => (),
    }

    msg.reply(&ctx, message).await?;
    let str = ron::to_string(&server_hashmap.clone());
    if let Ok(str) = str {
        let _ = tokio::fs::write("db/map.ron", str).await;
    }

    Ok(())
}

#[command]
async fn map(ctx: &Context, msg: &Message) -> CommandResult {
    let guild_id = get_guild!(msg, ctx);

    let mut options = msg.content.split(' ');
    if !check_command(options.next(), "!!map") {
        return Ok(());
    }

    // Get id
    let id = get_id!(options, msg, ctx, "map");
    if check_mapping_exist(&guild_id, id).await {
        const MESSAGE: &str = "Identifier already exists. `Usage: !!remap <id> <content>`";
        dbg!(&MESSAGE);
        let _ = msg.reply(&ctx, MESSAGE).await;
        return Ok(());
    }

    let content = get_content!(options, msg, ctx, "map");
    let message = format!("Mapped `!!{id}` to `{content}`. You can use `!!{id}`");

    let mut server_hashmap = HASHMAP.lock().await;
    let hashmap = server_hashmap.get_mut(&guild_id);
    match hashmap {
        Some(hashmap) => {
            hashmap.insert(String::from(id), content);
        }
        None => {
            server_hashmap.insert(guild_id, HashMap::from([(String::from(id), content)]));
        }
    }

    let _ = msg.reply(&ctx, message).await;
    let str = ron::to_string(&server_hashmap.clone());
    if let Ok(str) = str {
        let _ = tokio::fs::write("db/map.ron", str).await;
    }

    Ok(())
}

#[command]
async fn delete(ctx: &Context, msg: &Message) -> CommandResult {
    let guild_id = get_guild!(msg, ctx);

    let mut options = msg.content.split(' ');
    if !check_command(options.next(), "!!delete") {
        return Ok(());
    }

    // Get id
    let id = get_id!(options, msg, ctx, "delete", false);
    if !check_mapping_exist(&guild_id, id).await {
        const MESSAGE: &str = "Identifier doesn't exist.";
        dbg!(&MESSAGE);
        let _ = msg.reply(&ctx, MESSAGE).await;
        return Ok(());
    }

    let message = format!("Deleted `!!{id}`");

    let mut server_hashmap = HASHMAP.lock().await;
    let hashmap = server_hashmap.get_mut(&guild_id);
    match hashmap {
        Some(hashmap) => {
            hashmap.remove(id);
        }
        None => (),
    }

    let _ = msg.reply(&ctx, message).await;
    let str = ron::to_string(&server_hashmap.clone());
    if let Ok(str) = str {
        let _ = tokio::fs::write("db/map.ron", str).await;
    }

    Ok(())
}

#[command]
async fn help(ctx: &Context, msg: &Message) -> CommandResult {
    let _ = msg.reply(&ctx, "TODO: Help message").await;
    Ok(())
}
