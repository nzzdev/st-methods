  function jenks(data, n_classes) {
    if (n_classes > data.length) return null;

    data = data.slice().sort(function(a, b) {
      return a - b;
    });

    var matrices = getMatrices(data, n_classes);
    var lower_class_limits = matrices.lower_class_limits;

    // extract n_classes out of the computed matrices
    return breaks(data, lower_class_limits, n_classes);
  }

  /**
   * the second part of the jenks recipe: take the calculated
   * matricesand derive an array of n breaks.
   */
  function breaks(data, lower_class_limits, n_classes) {
    var k = data.length - 1,
      kclass = [],
      countNum = n_classes;

    // the calculation of classes will never include the upper and
    // lower bounds, so we need to explicitly set them
    kclass[n_classes] = data[data.length - 1];
    kclass[0] = data[0];

    // the lower_class_limits matrix is used as indexes into itself
    // here: the `k` variable is reused in each iteration.
    while (countNum > 1) {
      kclass[countNum - 1] = data[lower_class_limits[k][countNum] - 2];
      k = lower_class_limits[k][countNum] - 1;
      countNum--;
    }

    return kclass;
  }

  /**
   * Compute the matrices required for Jenks breaks. These matrices
   * can be used for any classing of data with `classes <= n_classes`
   */
  function getMatrices(data, n_classes) {
    // * lower_class_limits (LC): optimal lower class limits
    // * variance_combinations (OP): optimal variance combinations for all classes
    var lower_class_limits = [],
      variance_combinations = [],
      i,
      j,
      variance = 0;

    // Initialize matrix's
    for (i = 0; i < data.length + 1; i++) {
      var tmp1 = [],
        tmp2 = [];
      for (j = 0; j < n_classes + 1; j++) {
        tmp1.push(0);
        tmp2.push(0);
      }
      lower_class_limits.push(tmp1);
      variance_combinations.push(tmp2);
    }

    for (i = 1; i < n_classes + 1; i++) {
      lower_class_limits[1][i] = 1;
      variance_combinations[1][i] = 0;
      for (j = 2; j < data.length + 1; j++) {
        variance_combinations[j][i] = Infinity;
      }
    }

    for (var l = 2; l < data.length + 1; l++) {
      var sum = 0,
        sum_squares = 0,
        w = 0,
        i4 = 0;

      for (var m = 1; m < l + 1; m++) {
        var lower_class_limit = l - m + 1,
          val = data[lower_class_limit - 1];

        // here we're estimating variance for each potential classing
        // of the data, for each potential number of classes. `w`
        // is the number of data points considered so far.
        w++;
        sum += val;
        sum_squares += val * val;
        variance = sum_squares - (sum * sum) / w;
        i4 = lower_class_limit - 1;

        if (i4 === 0) {
          continue;
        }

        for (j = 2; j < n_classes + 1; j++) {
          // if adding this element to an existing class
          // will increase its variance beyond the limit, break
          // the class at this point, setting the lower_class_limit
          // at this point.
          if (
            variance_combinations[l][j] >=
            variance + variance_combinations[i4][j - 1]
          ) {
            lower_class_limits[l][j] = lower_class_limit;
            variance_combinations[l][j] =
              variance + variance_combinations[i4][j - 1];
          }
        }
      }

      lower_class_limits[l][1] = 1;
      variance_combinations[l][1] = variance;
    }

    return {
      lower_class_limits: lower_class_limits,
      variance_combinations: variance_combinations
    };
  }

exports.jenks = jenks