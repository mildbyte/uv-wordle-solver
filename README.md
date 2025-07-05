# Wordle solver that uses uv's dependency resolver

Code for my blog post, [Solving Wordle with uv's dependency resolver](https://mildbyte.xyz/blog/solving-wordle-with-uv-dependency-resolver/) - read how it works there

## Running

Get [`uv`](https://docs.astral.sh/uv/) and run the solver as follows:

```
uv run main.py run --no-suppress --no-emit-project

Using CPython 3.10.12 interpreter at: /usr/bin/python
warning: No `requires-python` value found in the workspace. Defaulting to `>=3.10`.
Resolved 33 packages in 579ms
GUESS: later
> YYY..
Using CPython 3.10.12 interpreter at: /usr/bin/python
warning: No `requires-python` value found in the workspace. Defaulting to `>=3.10`.
Resolved 41 packages in 1.79s
Added wordle-a-in-1345 v1
Added wordle-a-in-2 v0
Updated wordle-a-poss v8 -> v2
Added wordle-e-in-45 v0
Updated wordle-e-poss v2 -> v4
Added wordle-l-in-1 v0
Added wordle-l-in-2345 v1
Updated wordle-l-poss v16 -> v1
Updated wordle-pos-1 v12 -> v19
Updated wordle-pos-2 v1 -> v20
Updated wordle-pos-3 v20 -> v5
Updated wordle-pos-4 v5 -> v1
Updated wordle-pos-5 v18 -> v12
Added wordle-r-in-45 v0
Updated wordle-r-poss v1 -> v0
Updated wordle-s-poss v0 -> v16
Added wordle-t-in-1245 v1
Added wordle-t-in-3 v0
Updated wordle-t-poss v4 -> v8
Updated wordle-word v2308 -> v2296
GUESS: steal
> GG.YG
Using CPython 3.10.12 interpreter at: /usr/bin/python
warning: No `requires-python` value found in the workspace. Defaulting to `>=3.10`.
Resolved 47 packages in 1.23s
Added wordle-a-in-3 v1
Added wordle-a-in-4 v0
Updated wordle-a-poss v2 -> v4
Added wordle-e-in-3 v0
Updated wordle-e-poss v4 -> v0
Added wordle-l-in-5 v1
Updated wordle-l-poss v1 -> v3
Updated wordle-pos-3 v5 -> v1
Updated wordle-pos-4 v1 -> v12
Added wordle-s-in-1 v1
Added wordle-t-in-2 v1
Updated wordle-word v2296 -> v531
GUESS: stall
> GGGGG
Hooray!
```
