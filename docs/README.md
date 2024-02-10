>State the obvious, I didn't get my perfect fantasy

DALL-E 3 is OpenAI's latest text-to-image system. One of its features is that it leverages OpenAI's GPT to "automatically generate tailored, detailed prompts that bring your idea to life." In other words, it revises your prompt before generating an image. While this feature is meant to minimize prompt engineering by the user, I still found myself struggling to communicate with DALL-E 3 in a way that produced reliable results. Below are some of the lessons I learned working with four fellow Swifties to visualize:

- New Romantics as Pop Art for Lauren
- Fearless as an Afrofuturist textile for Evelyn
- Now That We Don't Talk as a Slim Aarons photograph for Haleigh
- New Year's Day as Art Nouveau for Sarah

## In the Style Of

I started with simple prompts that asked for an image in a ```style``` that represented ```lyrics```. The style was typically two-to-three words, and I provided the entire lyrics of the song. While the results were in the right ballpark, none were a home run.

To improve the images, I worked with each Swiftie to identify specific artists or artworks whose style we wanted to represent. The objective wasn't to produce an image that would pass as that of the artist, but instead to use the artist to identify fundamental features we wanted the image to include.

DALL-E 3, however, is designed to decline requests that ask for an image in the style of a living artist[^1]. Instead, DALL-E 3 replaces the reference with three adjectives that describe the artist's style. For example, if I asked for "Andy Warhol Pop Art," it revised the prompt to "vibrant, heavily saturated, and repetitive imagery that reflects the concept of Pop Art." To truly capture the style, though, I found much more detailed descriptions were needed. I initially crafted them manually from artist statements and reviews of their work, but I eventually shifted to using GPT to generate keywords for me.

While the results rarely looked like they came from the referenced artist's portfolio, I think they did capture the spirit of the artistic style.

### Fearless x Afrofuturist Textile

|Original Image|Final Image|
|--------------|-----------|
|![Fearless - Afrofuturist Textile](/assets/fearless-afrofuturist-textile.jpg){: width="425" }|![Fearless - Afrofuturist Textile](/assets/fearless-final.jpg){: width="425" }|
|*Prompt by me*<br/>An Afrofuturist textile with no text, words, or numbers that represents the following lyrics. I NEED it to not have any text.|*Prompt by me*\An Afrofuturist quilt that looks like a painting using African textiles and bright jewel tones and celebrates Black life with no text, words, or numbers that represents the following lyrics. I NEED it to not have any text.|
|*Revised propt by DALL-E 3*\An Afrofuturist textile design inspired by the story of a romantic encounter represented in a lyrical way. Imagine a piece of fabric that captures the essence of a rainy street scene with an ethereal glow. Visualize the exciting tension of a budding romance; the urge to dance fearlessly in a parking lot in the middle of a storm. Show this elation of running head-first, hand in hand, into a unknown yet thrilling journey. The textile should narrate the story of a romantic drive that captures a fearless first kiss, the courage it instills, and the unshakeable bond it creates. Importantly, the fabric should not contain any text, words or numbers.|*Revised prompt by DALL-E 3*\An Afrofuturist quilt artwork, inspired by African textiles with bold jewel tones. The vibrant quilt celebrates Black life, with no textual elements. To interpret the essence of the song, imagine a scene unfolds, depicting streets glistening after a rain shower; the glow is mirrored on the pavement. At the center of this scene, two figures stand in the middle of an illuminated parking lot. One figure, a Black woman in a beautiful dress, dances fearlessly amidst the storm, expressed through geometric and fluid designs. Another figure watches with admiration, their gestures suggesting a deep connection. A car in the background intensifies the urban narrative, in contrast with the traditional African textile elements of the quilt.|

## Text

I struggled to stop DALL-E 3 from including text -- which was commonly non-sensical combinations of things that looked like letters -- in the images. I experimented with different instructions, some of which were discarded in the revised prompt or included but ignored. This appears to be a common issue and frustration. In my opinion, it is the biggest obstacle to utilizing DALL-E 3 programatically.

Examples

## Photographs

I also found DALL-E 3 needed particular prompting to reliably generate photographic images. Unlike with text, I found the instruction ```I NEED it to be a photograph.``` to be consistently effective.

## Importance of a Pipeline

Above all else, I learned image generation is highly iterative. In search of perfection, I made many tweaks to my prompts and ended up producing XXX images. To make it easy on myself, I built a pipeline that uses OpenAI’s API and saves every original prompt, revised prompt, and corresponding image. That way, I didn’t lose any data and learned as much as possible from each iteration. I recommend anyone experimenting with generative AI do so programatically with logging.

---

[^1]: While OpenAI doesn't disclose its specific guidelines, users have "hacked" the system to get it to reveal its own rules, which [reportedly](https://the-decoder.com/dall-e-3s-system-prompt-reveals-openais-rules-for-generative-image-ai/) includes this instruction: ```Do not create images in the style of artists whose last work was created within the last 100 years (e.g. Picasso, Kahlo). Artists whose last work was over 100 years ago are ok to reference directly (e.g. Van Gogh, Klimt). If asked say, "I can't reference this artist", but make no mention of this policy. Instead, apply the following procedure when creating the captions for dalle: (a) substitute the artist's name with three adjectives that capture key aspects of the style; (b) include an associated artistic movement or era to provide context; and (c) mention the primary medium used by the artist.```