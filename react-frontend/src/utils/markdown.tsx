import hljs from 'highlight.js/lib/core';
import hljsPython from 'highlight.js/lib/languages/python';
import hljsBash from 'highlight.js/lib/languages/bash';
import hljsShell from 'highlight.js/lib/languages/shell';
import hljsGo from 'highlight.js/lib/languages/go';
import hljsHaskell from 'highlight.js/lib/languages/haskell';
import hljsRust from 'highlight.js/lib/languages/rust';
import hljsYaml from 'highlight.js/lib/languages/yaml';
import hljsJSON from 'highlight.js/lib/languages/json';
import hljsCSS from 'highlight.js/lib/languages/css';
import hljsMarkdown from 'highlight.js/lib/languages/markdown';
import hljsXML from 'highlight.js/lib/languages/xml';
import hljsDiff from 'highlight.js/lib/languages/diff';
import hljsIni from 'highlight.js/lib/languages/ini';
import hljsJavascript from 'highlight.js/lib/languages/javascript';
import hljsSQL from 'highlight.js/lib/languages/sql';
import hljsTypescript from 'highlight.js/lib/languages/typescript';
import hljsLatex from 'highlight.js/lib/languages/latex';
import hljsDockerfile from 'highlight.js/lib/languages/dockerfile';
import hljsNginx from 'highlight.js/lib/languages/nginx';

hljs.registerLanguage('python', hljsPython);
hljs.registerLanguage('bash', hljsBash);
hljs.registerLanguage('shell', hljsShell);
hljs.registerLanguage('go', hljsGo);
hljs.registerLanguage('haskell', hljsHaskell);
hljs.registerLanguage('rust', hljsRust);
hljs.registerLanguage('yaml', hljsYaml);
hljs.registerLanguage('json', hljsJSON);
hljs.registerLanguage('css', hljsCSS);
hljs.registerLanguage('markdown', hljsMarkdown);
hljs.registerLanguage('xml', hljsXML);
hljs.registerLanguage('diff', hljsDiff);
hljs.registerLanguage('ini', hljsIni);
hljs.registerLanguage('javascript', hljsJavascript);
hljs.registerLanguage('sql', hljsSQL);
hljs.registerLanguage('typescript', hljsTypescript);
hljs.registerLanguage('latex', hljsLatex);
hljs.registerLanguage('dockerfile', hljsDockerfile);
hljs.registerLanguage('nginx', hljsNginx);

export const highlighter = hljs;

export function mermaidPlugin(md: any) {
  const origRule = md.renderer.rules.fence.bind(md.renderer.rules);
  md.renderer.rules.fence = (tokens: any, idx: any, options: any, env: any, slf: any) => {
    const token = tokens[idx];
    if (token.info === 'mermaid') {
      const code = token.content.trim();
      return `<div class="mermaid">${code}</div>`;
    }

    // Other languages
    return origRule(tokens, idx, options, env, slf);
  };
}
