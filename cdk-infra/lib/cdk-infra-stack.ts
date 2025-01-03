import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as path from 'path';

export class CdkInfraStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Create a Lambda function from a Docker image
    const apiFunction = new lambda.DockerImageFunction(this, 'ApiFunction', {
      code: lambda.DockerImageCode.fromImageAsset('../image', {
        cmd: ["main.handler"]
      }),
      memorySize: 256,
      timeout: cdk.Duration.seconds(60),
      architecture: lambda.Architecture.ARM_64,
    });

    // Add a function URL to the Lambda
    const functionUrl = apiFunction.addFunctionUrl({
      authType: lambda.FunctionUrlAuthType.NONE, // This makes it publicly accessible
    });

    // Output the Function URL
    new cdk.CfnOutput(this, 'FunctionUrl', {
      value: functionUrl.url,
      description: 'URL for the Lambda function',
    });
  }
}