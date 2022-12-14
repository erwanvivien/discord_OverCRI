use std::collections::HashMap;
use std::env;

use serenity::async_trait;
use serenity::framework::standard::macros::{command, group};
use serenity::framework::standard::{CommandResult, StandardFramework};
use serenity::model::channel::Message;
use serenity::prelude::*;

use lazy_static::lazy_static;

#[group]
#[commands(ping)]
struct General;

struct Handler;

lazy_static! {
    static ref HASHMAP: Mutex<HashMap<String, String>> = {
        let m = ron::from_str("{}").expect("Could not parse starting state");

        Mutex::new(m)
    };
}

#[async_trait]
impl EventHandler for Handler {
    async fn message(&self, ctx: Context, msg: Message) {
        if !msg.content.starts_with("!!") {
            return;
        }

        // let tmp = HASHMAP.lock().await;
        // let value = tmp.get("Hihi".into());
        // let _ = tmp;

        if msg.content == "!!help" {
            if let Err(why) = msg.reply(&ctx, "TODO: Help message").await {
                println!("Error sending message: {:?}", why);
            }
        } else if msg.content.starts_with("!!map ") {
            // Skip the command
            let mut options = msg.content.split(" ").skip(1);
            // Get id
            let id = options.next();
            if id.is_none() {
                const MESSAGE: &str = "Missing identifier. `Usage: !!map <id> <content>`";
                let _ = msg.reply(&ctx, MESSAGE).await;
                return;
            }

            let id = id.unwrap();

            let hashmap = HASHMAP.lock().await;
            let value = hashmap.get(id);

            if value.is_some() {
                const MESSAGE: &str = "Missing identifier. `Usage: !!map <id> <content>`";
                dbg!(&MESSAGE);
                let _ = msg.reply(&ctx, MESSAGE).await;
                return;
            }

            let content = options.collect::<Vec<_>>();
            if content.len() == 0 {
                const MESSAGE: &str = "Missing content. `Usage: !!map <id> <content>`";
                dbg!(&MESSAGE);
                let _ = msg.reply(&ctx, MESSAGE).await;
                return;
            }

            let content = content.join(" ");
            let message = format!("Mapped {id} to `{content}`. You can use `!!{id}`");

            let mut hashmap = HASHMAP.lock().await;
            dbg!("All good");
            hashmap.insert(String::from(id), content);
            dbg!("All good");
            let _ = hashmap;

            dbg!("All good");

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
    dbg!(&token);
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
