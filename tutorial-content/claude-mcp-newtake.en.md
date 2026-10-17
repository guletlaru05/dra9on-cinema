---
title: "From One Sentence to a Sci-Fi Video with Claude + MCP"
slug: claude-mcp-newtake
date: 2026-10-17
category: Tutorials
tags: [Claude, MCP, Newtake, Seedance 2.5, AI Video]
description: "Give Claude a single sentence, and Newtake, connected through MCP, takes care of everything from shot planning to video generation. Here is the actual production process, the problems I ran into, and how I solved them."
---

# From One Sentence to a Sci-Fi Video with Claude + MCP

> This article is based on my firsthand experience working on a paid collaboration with Newtake.

The most time-consuming part of making an AI video happens **before** you press the Generate button: breaking the scene into shots, writing a prompt for each one, and choosing the model, aspect ratio, and duration.

With MCP, you can hand that process over to Claude. In this article, I will show you exactly how I turned a single-sentence request into a four-shot sci-fi scene.

---

## What Is MCP?

**MCP (Model Context Protocol)** is a standard that connects AI tools such as Claude to external services so they can use those services' features directly.

- Without MCP: Claude writes a prompt → I copy it → paste it into a video tool → configure the settings → generate the video.
- With MCP: Claude **calls the video tool's functions directly**. It creates a project, plans the shots, and runs the generation process.

My role is simply to be the director: set the direction and judge the results.

---

## What You Need

- **Claude** (in an environment that supports connectors/MCP connections)
- **A Newtake account**
- **The Newtake connector connected to Claude**

Once the connection is set up, you can use Newtake's features directly from your Claude conversation.

---

## STEP 1. Make a Single-Sentence Request

You do not need a complicated prompt. Just describe the scene you want in natural language.

```
Seoul in ruins at sunset. A female survivor in combat fatigues walks alone through the collapsed city.
Turn this into a four-shot cinematic sci-fi scene.
```

**Tips**
- The genre, time of day, main character, and mood are enough to get started.
- Specifying the number of shots helps produce more consistent results.

---

## STEP 2. Claude Plans the Shots

After receiving the request, Claude first breaks the scene down into shots. Here is the sequence it came up with this time.

| Shot | Framing | Purpose |
|---|---|---|
| SHOT 01 | Extreme wide shot (drone) | An establishing shot showing the entire ruined city |
| SHOT 02 | Low-angle tracking shot | A tension-building shot following only the walking combat boots |
| SHOT 03 | Dolly-in close-up | An emotional shot moving from the protagonist's face toward her eyes |
| SHOT 04 | Over-the-shoulder shot | A closing shot looking out at the city from the protagonist's perspective |

The sequence moves from wide → detail → emotion → back out to wide. It follows the same visual language a person would use when creating a storyboard.

---

## STEP 3. Generation Runs on the Newtake Canvas

Claude uses MCP to create a project in Newtake and arrange nodes on the canvas.

1. First, it creates a **reference image (anchor)**. This establishes the look of the protagonist and the setting.
2. A **shot node** is created for each shot, and video is generated using the reference image.
3. Finally, the shots are **combined into a single video.**

A progress card appears in Claude, while the Newtake canvas lets you watch the nodes fill up one by one in real time.

**Model used:** Seedance 2.5
**Available settings:** 4–30 seconds / 480p, 720p, or 1080p / selectable aspect ratio

---

## STEP 4. Review the Result

The result was a four-shot sci-fi scene about 30 seconds long. All I did was enter a single-sentence request and review the result.

> (Embed the finished video or Reel here)

---

## Problems and How to Solve Them

### 1. When Generation Is Rejected

An automated filter may block a request during generation. In my case, a request for a **drama scene with face close-ups and extensive dialogue** was rejected twice.

**How to solve it**
- Simplify the scene. Remove the dialogue and describe the space and atmosphere rather than focusing on the characters.
- Do not include the names of real people, well-known works, or characters.
- If a request is rejected, do not keep repeating it unchanged. Rephrase it and try again.

### 2. When Generation Takes a Long Time

Video generation takes several minutes. Sending the same request again while you wait can cause **duplicate generations**. Check the status on the progress card and wait.

### 3. When the Result Is Not What You Wanted

Ask Claude to revise individual shots.

```
For SHOT 03, move in more slowly and hold on the close-up of her eyes for 2 seconds.
```

---

## Recap

| Traditional workflow | MCP workflow |
|---|---|
| I handle all the shot breakdowns, prompts, and settings | Claude plans and executes the process |
| Copy and paste between different tools | Everything happens in one conversation |
| Time spent on repetitive tasks | Focus on setting the direction |

MCP is a way to **let Claude be your "hands" while keeping your own "eyes" on the work** in AI video production. It is especially well suited to concept tests and quick drafts, rather than a final production where you need to watch the quality closely all the way through.

---

**Try Newtake:** [newtake.com](https://www.newtake.com/?sourceId=NT920205)

**Related video:** [Instagram Reel — Claude × Newtake](https://www.instagram.com/reel/DelRHYDunY-/)
