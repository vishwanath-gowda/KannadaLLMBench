# RomanBench annotator-facing copy v1

Instruction identifier: `romanbench-annotation-v1`

This document freezes the critical wording used by the v1 validation UI. Any substantive wording change should increment the instruction identifier before collecting additional production annotations.

## Intro

> You will see a Kannada sentence and one version typed using English letters.
>
> Your job is only to answer two simple questions. There is no typing required.

## Question 1

> **Does the Roman text have the same meaning as the Kannada sentence?**
>
> Yes / No

Clarification:

> Small spelling differences are okay if the meaning is still clear.

## Question 2

> **Would you type Kannada this way using English letters?**
>
> Yes / No

Mandatory clarification:

> **Judge only the English-letter spelling/style. Do not judge whether the Kannada sentence itself is formal or colloquial.**

Expanded instruction:

> Imagine you are messaging someone in Kannada but using English letters. Answer Yes if this spelling is a plausible way you might type it.
>
> This is not a colloquialness question. A Kannada sentence may be formal or colloquial. Here you are judging only how Kannada is represented with English letters.

## Skip

> Skip if you do not understand the Kannada sentence well enough to judge it. Skipping is better than guessing.

## Independence

> Do not search online, use transliteration tools, use an AI assistant, or ask another person. We want your own judgment.

## Interpretation constraint for analysis/papers

A `Yes` answer to Question 2 means only that the annotator considers the displayed Roman spelling a plausible way they might type that Kannada content using English letters. It must not be reported as evidence that the underlying Kannada sentence is colloquial, conversational, grammatical, or culturally natural.
