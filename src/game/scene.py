def tmp_context(ctx):
    return ContextScaler(ctx)


class ContextScaler:

    """Context manager to perform scaled drawing"""

    def __init__(self, cairo_ctx, *context_func):

        """Work with cairo_ctx, applying optionnal context_func"""

        self.cairo_ctx = cairo_ctx
        self.context_func = context_func

    def __enter__(self):

        """Save context state and apply optionnal scaling"""

        self.cairo_ctx.save()
        for f in self.context_func:
            f(self.cairo_ctx)
        return self.cairo_ctx

    def __exit__(self, *args):

        """Restore context state"""

        self.cairo_ctx.restore()


class Scene:

    def __init__(self, cairo_ctx, *context_func):

        self.cairo_ctx = cairo_ctx
        self.context_func = context_func
        self.scale = ContextScaler(cairo_ctx, *context_func)

    def compose(self, *context_func):

        funcs = self.context_func + context_func
        return Scene(self.cairo_ctx, *funcs)

    def dist(self, dx, dy):

        """Convert game distances dx, dy to actual screen distances (pixels)"""

        with self.scale:
            w, h = self.cairo_ctx.user_to_device_distance(dx, dy)
        return w, h
