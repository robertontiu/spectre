/* The background field's renderer in a worker: it draws on the two transferred canvases,
   so the page's main thread does none of the field's drawing. */
import { FieldRenderer, type FieldMessage, type FieldReport } from "./field-renderer";

const scope = self as unknown as {
  postMessage: (m: FieldReport) => void;
  onmessage: ((e: MessageEvent<FieldMessage>) => void) | null;
};
let renderer: FieldRenderer | null = null;

scope.onmessage = (e) => {
  const m = e.data;
  if (m.type === "init") {
    renderer = new FieldRenderer(m.back, m.front, m.origin, m.adaptive, (r) => scope.postMessage(r), m.probe);
    return;
  }
  renderer?.handle(m);
};
scope.postMessage({ type: "hello" });
