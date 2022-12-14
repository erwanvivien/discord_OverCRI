use std::collections::HashMap;
use std::env;
use std::sync::Arc;

use serenity::async_trait;
use serenity::framework::standard::macros::{command, group};
use serenity::framework::standard::{CommandResult, StandardFramework};
use serenity::model::channel::Message;
use serenity::model::prelude::GuildId;
use serenity::prelude::*;

use lazy_static::lazy_static;

#[group]
#[commands(ping)]
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
            return;
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
            return;
        }

        id.unwrap()
    }};
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

        if msg.content == "!!help" {
            let _ = msg.reply(&ctx, "TODO: Help message").await;
        } else if msg.content.starts_with("!!map") {
            let mut options = msg.content.split(' ');
            if !check_command(options.next(), "!!map") {
                return;
            }

            // Get id
            let id = get_id!(options, msg, ctx, "map");
            if check_mapping_exist(&guild_id, id).await {
                const MESSAGE: &str = "Identifier already exists. `Usage: !!remap <id> <content>`";
                dbg!(&MESSAGE);
                let _ = msg.reply(&ctx, MESSAGE).await;
                return;
            }

            let content = get_content!(options, msg, ctx, "map");
            let message = format!("Mapped `!!{id}` to `{content}`. You can use `!!{id}`");

            let mut server_hashmap = HASHMAP.lock().await;
            let mut hashmap = server_hashmap.get(&guild_id).map(|x| x.to_owned());
            match &mut hashmap {
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
        } else if msg.content.starts_with("!!remap") {
            let mut options = msg.content.split(' ');
            if !check_command(options.next(), "!!remap") {
                return;
            }

            // Get id
            let id = get_id!(options, msg, ctx, "remap");
            if !check_mapping_exist(&guild_id, id).await {
                const MESSAGE: &str = "Identifier doesn't exist. `Usage: !!map <id> <content>`";
                dbg!(&MESSAGE);
                let _ = msg.reply(&ctx, MESSAGE).await;
                return;
            }

            let content = get_content!(options, msg, ctx, "remap");
            let message = format!("Remapped `!!{id}` to `{content}`. You can use `!!{id}`");

            // let mut hashmap = HASHMAP.lock().await;
            // hashmap.insert(String::from(id), content);

            let mut server_hashmap = HASHMAP.lock().await;
            let hashmap = server_hashmap.get_mut(&guild_id);
            match hashmap {
                Some(hashmap) => {
                    hashmap.insert(String::from(id), content);
                }
                None => (),
            }

            let _ = msg.reply(&ctx, message).await;
            let str = ron::to_string(&server_hashmap.clone());
            if let Ok(str) = str {
                let _ = tokio::fs::write("db/map.ron", str).await;
            }
        } else if msg.content.starts_with("!!delete") {
            let mut options = msg.content.split(' ');
            if !check_command(options.next(), "!!delete") {
                return;
            }

            // Get id
            let id = get_id!(options, msg, ctx, "delete", false);
            if !check_mapping_exist(&guild_id, id).await {
                const MESSAGE: &str = "Identifier doesn't exist.";
                dbg!(&MESSAGE);
                let _ = msg.reply(&ctx, MESSAGE).await;
                return;
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
        } else {
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

            let message = match value {
                Some(value) => value.clone(),
                None => format!("`!!{command}` does not exist"),
            };

            let _ = msg.reply(&ctx, message).await;
        }
    }
}

#[tokio::main]
async fn main() {
    let framework = StandardFramework::new()
        .configure(|c| c.prefix("~")) // set the bot's prefix to "~"
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
    dbg!(&msg);
    msg.reply(ctx, "Pong!").await?;

    Ok(())
}
