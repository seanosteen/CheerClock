![Cheer Clock Time-Lapse](content/CheerClock_v1.GIF)
# Cheer Clock v1 November, 2022

The [Pimoroni Galactic Unicorn](https://shop.pimoroni.com/products/galactic-unicorn?variant=40057440960595) is a
fantastic LED reader board! It covers much of your tinkering needs. This code sample allows you to program the
included 
[Raspberry Pi PICO W](https://www.raspberrypi.com/products/raspberry-pi-pico/) to do a couple of
really cool IoT things:
* Create a bright, easy to read, Internet synchronized clock, for your desk or workbench
* Tune into the global "mood ring" that is the [Cheerlights Community](https://cheerlights.com/). Set your clock's
  background color to the same color as thousands of other devices around the world.

## What's in this GitHub repository:
* [MicroPython Code](./MicroPython/) - The source code for the clock shown above.
* [Laser-cut templates](./Case_Template/) - The SVG files for the box-joint case and the acrylic diffuser grill.

![Display Case](./content/GalacticUnicorn_BoxJoint_Case_3mm_ply.png)

![Case](./content/box_joint_case.png)
![Grill](./content/diffuser_grill.png)

## Future enhancements
1. Add a countdown timer functionality. I use an egg timer regularly at my desk for Pomodoro type focus sprints. 
I'd like to use the builtin buttons on the Galactic Unicorn to set timers quickly and have the built-in speaker
play a MIDI tune when the timer ends.

2. Add a message board reader. The message loop will listen on an MQTT channel for events fired from other applications.
The message will be displayed, then resume acting like a clock.


I'll work on these on a future sprint, but if anyone wants to collaborate on those additions, I'd be really 
excited to work with you!

