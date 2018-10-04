import * as React from "react";
import { render } from "react-dom";

import { Hello } from './hello';

render(<Hello compiler="Typescript" framework="React" bundler="Webpack" />,

document.getElementById('root'));